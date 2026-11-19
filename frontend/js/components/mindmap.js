// Interactive Mind Map Component with SVG rendering, Pan/Zoom, Collapsible Nodes & PNG Export

class MindMapViewer {
  constructor(containerId) {
    this.container = document.getElementById(containerId);
    this.scale = 1.0;
    this.translateX = 100;
    this.translateY = 300;
    this.isDragging = false;
    this.startX = 0;
    this.startY = 0;
    this.data = null;
    this.svg = null;
    this.g = null;
  }

  render(data) {
    this.data = data;
    this.container.innerHTML = '';
    
    // Create toolbar
    const toolbar = document.createElement('div');
    toolbar.className = 'mindmap-toolbar';
    toolbar.innerHTML = `
      <button class="btn btn-sm" id="mm-zoom-in" title="Zoom In">🔍 +</button>
      <button class="btn btn-sm" id="mm-zoom-out" title="Zoom Out">🔍 -</button>
      <button class="btn btn-sm" id="mm-reset" title="Reset View">🎯 重置 / Reset</button>
      <button class="btn btn-sm" id="mm-export" title="Export PNG">📷 导出图片 / Export</button>
    `;
    this.container.appendChild(toolbar);

    // Create SVG
    this.svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    this.svg.setAttribute('width', '100%');
    this.svg.setAttribute('height', '100%');
    this.svg.style.cursor = 'grab';

    this.g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
    this.svg.appendChild(this.g);
    this.container.appendChild(this.svg);

    this.setupEvents(toolbar);
    this.draw();
  }

  setupEvents(toolbar) {
    toolbar.querySelector('#mm-zoom-in').onclick = () => this.zoom(1.2);
    toolbar.querySelector('#mm-zoom-out').onclick = () => this.zoom(0.8);
    toolbar.querySelector('#mm-reset').onclick = () => {
      this.scale = 1.0;
      this.translateX = 120;
      this.translateY = this.container.clientHeight / 2;
      this.updateTransform();
    };
    toolbar.querySelector('#mm-export').onclick = () => this.exportPNG();

    this.svg.onmousedown = (e) => {
      this.isDragging = true;
      this.startX = e.clientX - this.translateX;
      this.startY = e.clientY - this.translateY;
      this.svg.style.cursor = 'grabbing';
    };

    window.onmousemove = (e) => {
      if (!this.isDragging) return;
      this.translateX = e.clientX - this.startX;
      this.translateY = e.clientY - this.startY;
      this.updateTransform();
    };

    window.onmouseup = () => {
      if (this.isDragging) {
        this.isDragging = false;
        if (this.svg) this.svg.style.cursor = 'grab';
      }
    };

    this.container.onwheel = (e) => {
      e.preventDefault();
      const zoomFactor = e.deltaY < 0 ? 1.1 : 0.9;
      this.zoom(zoomFactor);
    };
  }

  zoom(factor) {
    this.scale = Math.max(0.3, Math.min(3.0, this.scale * factor));
    this.updateTransform();
  }

  updateTransform() {
    if (this.g) {
      this.g.setAttribute('transform', `translate(${this.translateX}, ${this.translateY}) scale(${this.scale})`);
    }
  }

  draw() {
    if (!this.data) return;
    this.g.innerHTML = '';
    
    // Layout hierarchy
    const layout = this.computeTreeLayout(this.data);
    
    // Draw links first
    layout.links.forEach(link => {
      const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
      const d = `M ${link.source.x} ${link.source.y} C ${link.source.x + 80} ${link.source.y}, ${link.target.x - 80} ${link.target.y}, ${link.target.x} ${link.target.y}`;
      path.setAttribute('d', d);
      path.setAttribute('fill', 'none');
      path.setAttribute('stroke', '#94a3b8');
      path.setAttribute('stroke-width', '2');
      this.g.appendChild(path);
    });

    // Draw nodes
    layout.nodes.forEach(node => {
      const gNode = document.createElementNS('http://www.w3.org/2000/svg', 'g');
      gNode.setAttribute('transform', `translate(${node.x}, ${node.y})`);
      gNode.style.cursor = 'pointer';

      const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
      const paddingX = 16;
      const paddingY = 8;
      const textWidth = Math.min(260, node.title.length * 14 + 20);
      
      rect.setAttribute('x', -10);
      rect.setAttribute('y', -20);
      rect.setAttribute('width', textWidth);
      rect.setAttribute('height', 40);
      rect.setAttribute('rx', '8');
      
      // Node styling based on depth
      if (node.depth === 0) {
        rect.setAttribute('fill', '#2563eb');
        rect.setAttribute('stroke', '#1d4ed8');
      } else if (node.depth === 1) {
        rect.setAttribute('fill', '#0284c7');
        rect.setAttribute('stroke', '#0369a1');
      } else {
        rect.setAttribute('fill', '#f8fafc');
        rect.setAttribute('stroke', '#cbd5e1');
      }
      rect.setAttribute('stroke-width', '1.5');
      rect.setAttribute('filter', 'drop-shadow(0 2px 4px rgba(0,0,0,0.06))');

      const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
      text.setAttribute('x', 6);
      text.setAttribute('y', 5);
      text.setAttribute('fill', node.depth < 2 ? '#ffffff' : '#1e293b');
      text.setAttribute('font-size', node.depth === 0 ? '15px' : '13px');
      text.setAttribute('font-weight', node.depth < 2 ? '600' : '400');
      text.textContent = node.title.length > 20 ? node.title.slice(0, 19) + '…' : node.title;

      gNode.appendChild(rect);
      gNode.appendChild(text);

      if (node.notes) {
        const titleEl = document.createElementNS('http://www.w3.org/2000/svg', 'title');
        titleEl.textContent = `${node.title}\n${node.notes}`;
        gNode.appendChild(titleEl);
      }

      this.g.appendChild(gNode);
    });

    this.updateTransform();
  }

  computeTreeLayout(root) {
    const nodes = [];
    const links = [];
    let currentY = -250;

    function traverse(node, depth, x, parent) {
      const nodeObj = {
        title: node.title || 'Untitled',
        notes: node.notes || '',
        depth,
        x,
        y: currentY
      };
      nodes.push(nodeObj);
      
      if (parent) {
        links.push({ source: parent, target: nodeObj });
      }

      currentY += 60;

      if (node.children && node.children.length > 0) {
        node.children.forEach(child => {
          traverse(child, depth + 1, x + 240, nodeObj);
        });
      }
    }

    traverse(root, 0, 0, null);
    return { nodes, links };
  }

  exportPNG() {
    const serializer = new XMLSerializer();
    const svgStr = serializer.serializeToString(this.svg);
    const canvas = document.createElement('canvas');
    canvas.width = 1600;
    canvas.height = 1200;
    const ctx = canvas.getContext('2d');
    const img = new Image();
    img.src = 'data:image/svg+xml;base64,' + btoa(unescape(encodeURIComponent(svgStr)));
    img.onload = () => {
      ctx.fillStyle = '#ffffff';
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      ctx.drawImage(img, 0, 0);
      const link = document.createElement('a');
      link.download = `mindmap-${Date.now()}.png`;
      link.href = canvas.toDataURL('image/png');
      link.click();
    };
  }
}
