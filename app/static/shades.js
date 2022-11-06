function rbgToHex(r, g, b) {
  return "#" + ((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1);
}

function hexToRgb(hex) {
  var result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  return result
    ? {
        r: parseInt(result[1], 16),
        g: parseInt(result[2], 16),
        b: parseInt(result[3], 16),
      }
    : null;
}

function generate(r, g, b, n) {
  let colors = [];
  let inc = Math.floor(256 / n);
  for (var i = 0; i < n; i++) {
    r += 33;
    r %= 255;
    g += 33;
    g %= 255;
    b += 33;
    b %= 255;
    colors.push(rbgToHex(r, g, b));
  }
  return colors;
}

function generateShades(hex, n) {
  let { r, g, b } = hexToRgb(hex);

  return generate(r, g, b, n);
}
