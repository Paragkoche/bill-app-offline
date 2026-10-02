const fs = require('fs');
const path = require('path');

const distJsDir = path.join(__dirname, '..', 'static', 'dist', 'js');
if (!fs.existsSync(distJsDir)) {
  fs.mkdirSync(distJsDir, { recursive: true });
}

// 1. Copy flowbite.min.js from node_modules
const flowbiteSrc = path.join(__dirname, '..', 'node_modules', 'flowbite', 'dist', 'flowbite.min.js');
const flowbiteDest = path.join(distJsDir, 'flowbite.min.js');

if (fs.existsSync(flowbiteSrc)) {
  fs.copyFileSync(flowbiteSrc, flowbiteDest);
  console.log('✓ Copied flowbite.min.js -> static/dist/js/flowbite.min.js');
}

// 2. Copy any custom js from static/src to static/dist/js
const srcJsDir = path.join(__dirname, '..', 'static', 'src');
if (fs.existsSync(srcJsDir)) {
  const files = fs.readdirSync(srcJsDir);
  for (const file of files) {
    if (file.endsWith('.js')) {
      fs.copyFileSync(path.join(srcJsDir, file), path.join(distJsDir, file));
      console.log(`✓ Copied ${file} -> static/dist/js/${file}`);
    }
  }
}

console.log('JS build complete.');
