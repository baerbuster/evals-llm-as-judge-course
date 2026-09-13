<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 340" width="100%">
  <rect x="0" y="0" width="800" height="340" fill="#ffffff"/>
  <text x="40" y="36" font-family="sans-serif" font-size="22" fill="#000000">two pulls on one prompt</text>
  <rect x="290" y="50" width="220" height="60" fill="#ffffff" stroke="#000000"/>
  <text x="400" y="88" font-family="sans-serif" font-size="18" fill="#000000" text-anchor="middle">judge prompt</text>
  <line x1="200" y1="168" x2="330" y2="110" stroke="#000000"/>
  <path d="M 330,110 L 319.6,121.2 L 314.8,110.2 Z" fill="#000000"/>
  <line x1="600" y1="168" x2="470" y2="110" stroke="#000000"/>
  <path d="M 470,110 L 480.4,121.2 L 485.2,110.2 Z" fill="#000000"/>
  <text x="185" y="132" font-family="sans-serif" font-size="18" fill="#000000">narrow</text>
  <text x="560" y="132" font-family="sans-serif" font-size="18" fill="#000000">widen</text>
  <rect x="30" y="170" width="330" height="140" fill="#ffffff" stroke="#000000"/>
  <text x="50" y="205" font-family="sans-serif" font-size="18" fill="#c62828">false positive</text>
  <text x="50" y="235" font-family="sans-serif" font-size="18" fill="#000000">output 14</text>
  <text x="50" y="263" font-family="sans-serif" font-size="18" fill="#000000">judge FAIL, you PASS</text>
  <text x="50" y="295" font-family="sans-serif" font-size="18" fill="#000000">fix: narrow FAIL</text>
  <rect x="440" y="170" width="330" height="140" fill="#ffffff" stroke="#000000"/>
  <text x="460" y="205" font-family="sans-serif" font-size="18" fill="#c62828">false negative</text>
  <text x="460" y="235" font-family="sans-serif" font-size="18" fill="#000000">output 6</text>
  <text x="460" y="263" font-family="sans-serif" font-size="18" fill="#000000">judge PASS, you FAIL</text>
  <text x="460" y="295" font-family="sans-serif" font-size="18" fill="#000000">fix: widen FAIL</text>
</svg>
Output 14 asks you to narrow what counts as a failure and output 6 asks you to widen it, so the two fixes pull the same judge prompt in opposite directions.
