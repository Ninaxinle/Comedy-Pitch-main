import { PosterGenerator } from '../utils/posterGenerator';

export interface Video {
  id: string;
  title: string;
  description: string;
  duration: number; // in seconds
  isPublic: boolean;
  likes: number;
  overallScore: number; // 0-5 scale
  thumbnail: string;
  uploadDate: string;
  views: number;
}

class VideoService {
  // Helper function to generate random duration (5-20 minutes)
  private generateDuration(): number {
    return Math.floor(Math.random() * 900) + 300; // 300-1200 seconds (5-20 minutes)
  }

  // Helper function to generate random public/private status
  private generatePublicStatus(): boolean {
    return Math.random() > 0.3; // 70% chance of being public
  }

  // Helper function to generate random upload date
  private generateUploadDate(): string {
    const now = new Date();
    const daysAgo = Math.floor(Math.random() * 30) + 1; // 1-30 days ago
    const uploadDate = new Date(now.getTime() - (daysAgo * 24 * 60 * 60 * 1000));
    return uploadDate.toISOString();
  }

  // Helper function to generate description
  private generateDescription(): string {
    const descriptions = [
      "A hilarious stand-up performance that will have you laughing from start to finish.",
      "Comedy gold! This performance showcases incredible timing and wit.",
      "An amazing comedy set with clever observations and sharp punchlines.",
      "Pure entertainment! This stand-up routine is packed with laughs.",
      "A brilliant comedy performance that demonstrates masterful storytelling.",
      "Laugh-out-loud funny! This set is a perfect blend of humor and heart."
    ];
    return descriptions[Math.floor(Math.random() * descriptions.length)];
  }



  // Helper function to extract title from filename
  private extractTitleFromFilename(filename: string): string {
    // Remove file extension
    const nameWithoutExt = filename.replace(/\.(mp4|avi|mov|mkv)$/i, '');
    
    // The filenames are now clean, so we just return the name without extension
    // No need for special character handling since we've renamed the files
    return nameWithoutExt;
  }

  async getUserVideos(): Promise<Video[]> {
    try {
      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 500));
      
      console.log('API Call: GET /api/videos');

      const videos: Video[] = [];
      let videoId = 1;

      // Only show videos that the user has actually uploaded to the assets folder
      // We'll skip the mock data videos since those aren't the user's uploads

      // Add dynamically detected video files from assets folder
      const assetVideos = [
        "Becoming a Corrupt Religious Leader Is Easy - Noah Gardenswartz - Stand-Up Featuring.mp4",
        "Black Music Tells You Everything You Need to Know - Roy Wood Jr..mp4",
        "Astrology Solves All of Your Problems - Julia Shiplett - Stand-Up Featuring.mp4",
        "Bill Burr - I'll Never Own a Helicopter - Full Special.mp4",
        "Aziz Ansari - Dangerously Delicious - Texting With Girls.mp4",
        "Auguste White's New Revenge Personality - Stand-Up Featuring.mp4"
      ];

      for (const videoFile of assetVideos) {
        try {
          // Check if the video file exists by trying to fetch it
          const videoResponse = await fetch(`/assets/${videoFile}`);
          
          if (videoResponse.ok) {
            const title = this.extractTitleFromFilename(videoFile);
            
            // Check if we already have this video from mock data
            const existingVideo = videos.find(v => v.title === title);
            if (!existingVideo) {
              const duration = this.generateDuration();
              const isPublic = this.generatePublicStatus();
              const overallScore = Math.round((Math.random() * 4 + 1) * 10) / 10;
              
              // Generate custom poster for this video
              const posterDataURL = PosterGenerator.generatePosterDataURL({
                title: title,
                score: overallScore,
                duration: duration,
                isPublic: isPublic
              });
              
              const video: Video = {
                id: videoId.toString(),
                title: title,
                description: this.generateDescription(),
                duration: duration,
                isPublic: isPublic,
                likes: Math.floor(Math.random() * 1000) + 50,
                overallScore: overallScore,
                thumbnail: posterDataURL,
                uploadDate: this.generateUploadDate(),
                views: Math.floor(Math.random() * 10000) + 500
              };
              
              videos.push(video);
              videoId++;
            }
          }
        } catch (error) {
          console.warn(`Asset video ${videoFile} not accessible:`, error);
        }
      }

      // Sort by upload date (newest first)
      return videos.sort((a, b) => new Date(b.uploadDate).getTime() - new Date(a.uploadDate).getTime());
    } catch (error) {
      console.error('Error loading videos:', error);
      return [];
    }
  }

  async getVideoById(id: string): Promise<Video | null> {
    try {
      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 300));
      
      console.log(`API Call: GET /api/videos/${id}`);

      const videos = await this.getUserVideos();
      return videos.find(video => video.id === id) || null;
    } catch (error) {
      console.error(`Error fetching video ${id}:`, error);
      return null;
    }
  }

  async getPublicVideos(): Promise<Video[]> {
    try {
      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 400));
      
      console.log('API Call: GET /api/videos/public');

      const videos = await this.getUserVideos();
      return videos.filter(video => video.isPublic);
    } catch (error) {
      console.error('Error fetching public videos:', error);
      return [];
    }
  }
}

export const videoService = new VideoService(); 