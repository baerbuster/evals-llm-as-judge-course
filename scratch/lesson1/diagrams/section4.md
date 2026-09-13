<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 320" width="100%">
  <rect x="0" y="0" width="800" height="320" fill="#ffffff"/>
  <text x="400" y="36" font-family="sans-serif" font-size="22" fill="#000000" text-anchor="middle">run 5 failures into buckets</text>
  <rect x="40" y="80" width="250" height="64" fill="#ffffff" stroke="#000000" stroke-width="2"/>
  <text x="56" y="106" font-family="sans-serif" font-size="18" fill="#000000">output 11</text>
  <text x="56" y="132" font-family="sans-serif" font-size="18" fill="#c62828">no_preamble FAIL</text>
  <rect x="40" y="180" width="250" height="90" fill="#ffffff" stroke="#000000" stroke-width="2"/>
  <text x="56" y="206" font-family="sans-serif" font-size="18" fill="#000000">output 0</text>
  <text x="56" y="232" font-family="sans-serif" font-size="18" fill="#c62828">shape FAIL</text>
  <text x="56" y="258" font-family="sans-serif" font-size="18" fill="#c62828">no_preamble FAIL</text>
  <rect x="520" y="70" width="240" height="50" fill="#ffffff" stroke="#000000" stroke-width="2"/>
  <text x="540" y="102" font-family="sans-serif" font-size="18" fill="#000000">wrong_shape</text>
  <rect x="520" y="150" width="240" height="50" fill="#ffffff" stroke="#000000" stroke-width="2"/>
  <text x="540" y="182" font-family="sans-serif" font-size="18" fill="#000000">preamble</text>
  <rect x="520" y="230" width="240" height="50" fill="#ffffff" stroke="#000000" stroke-width="2"/>
  <text x="540" y="262" font-family="sans-serif" font-size="18" fill="#000000">copied</text>
  <line x1="290" y1="112" x2="508" y2="172" stroke="#000000" stroke-width="2"/>
  <path d="M516,175 L498,174 L504,160 Z" fill="#000000"/>
  <line x1="290" y1="225" x2="508" y2="101" stroke="#000000" stroke-width="2"/>
  <path d="M516,97 L498,98 L505,112 Z" fill="#000000"/>
  <text x="400" y="305" font-family="sans-serif" font-size="18" fill="#000000" text-anchor="middle">shape is first</text>
</svg>
Output 11 fails one rule and lands in preamble, while output 0 fails two and lands in the bucket of the first rule in the fixed order.
