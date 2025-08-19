// Video Poster Generator
// Generates custom SVG posters for each video based on title and metadata

interface PosterConfig {
  title: string;
  performer?: string;
  score?: number;
  duration?: number;
  isPublic?: boolean;
}

export class PosterGenerator {
  private static readonly COLORS = {
    primary: ['#2d2d2d', '#404040', '#525252', '#666666', '#7a7a7a'],
    secondary: ['#1f1f1f', '#2f2f2f', '#3f3f3f', '#4a4a4a'],
    accent: ['#dc2626', '#ef4444', '#f87171', '#fca5a5'] // Red accent colors
  };

  private static getRandomColor(colors: string[]): string {
    return colors[Math.floor(Math.random() * colors.length)];
  }

  private static extractPerformer(title: string): string {
    // Try to extract performer name from title
    const patterns = [
      /^(.+?)\s*[-–—]\s*(.+)/, // "Performer - Title"
      /^(.+?)\s*[:：]\s*(.+)/, // "Performer: Title"
      /^(.+?)\s*["""]\s*(.+)/, // "Performer "Title""
    ];

    for (const pattern of patterns) {
      const match = title.match(pattern);
      if (match && match[1].length < 50) {
        return match[1].trim();
      }
    }

    // If no pattern matches, take first part before common words
    const firstPart = title.split(/[-–—:：]/)[0].trim();
    if (firstPart.length < 30) {
      return firstPart;
    }

    return 'Comedy Performance';
  }

  private static truncateTitle(title: string, maxLength: number = 40): string {
    if (title.length <= maxLength) return title;
    return title.substring(0, maxLength - 3) + '...';
  }

  static generatePoster(config: PosterConfig): string {
    const { title } = config;
    const performer = config.performer || this.extractPerformer(title);
    const truncatedTitle = this.truncateTitle(title);
    const truncatedPerformer = this.truncateTitle(performer, 25);

    const posterSvg = `
      <svg width="320" height="180" viewBox="0 0 320 180" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style="stop-color:${this.getRandomColor(this.COLORS.primary)};stop-opacity:1" />
            <stop offset="100%" style="stop-color:${this.getRandomColor(this.COLORS.secondary)};stop-opacity:1" />
          </linearGradient>
          <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
            <feDropShadow dx="1" dy="2" stdDeviation="2" flood-color="rgba(0,0,0,0.5)"/>
          </filter>
        </defs>
        
        <!-- Background -->
        <rect width="320" height="180" fill="url(#bg)"/>
        
        <!-- Red Spotlight Effect (similar to header) -->
        <circle cx="160" cy="90" r="80" fill="url(#redSpotlight)" opacity="0.3"/>
        <defs>
          <radialGradient id="redSpotlight" cx="50%" cy="50%" r="50%">
            <stop offset="0%" style="stop-color:#dc2626;stop-opacity:0.4" />
            <stop offset="70%" style="stop-color:#dc2626;stop-opacity:0.2" />
            <stop offset="100%" style="stop-color:#dc2626;stop-opacity:0" />
          </radialGradient>
        </defs>
        
        <!-- Main content -->
        <g filter="url(#shadow)">
          <!-- Performer name -->
          <text x="160" y="85" font-family="Arial, sans-serif" font-size="18" fill="white" text-anchor="middle" font-weight="bold">
            ${truncatedPerformer}
          </text>
          
          <!-- Title -->
          <text x="160" y="110" font-family="Arial, sans-serif" font-size="14" fill="#e5e5e5" text-anchor="middle">
            ${truncatedTitle}
          </text>
        </g>
      </svg>
    `;

    return posterSvg;
  }

  static generatePosterDataURL(config: PosterConfig): string {
    const svg = this.generatePoster(config);
    const encodedSvg = encodeURIComponent(svg);
    return `data:image/svg+xml;charset=utf-8,${encodedSvg}`;
  }
} 