// Mock S3 Service - simulates S3 calls but serves from local storage
export interface S3Video {
  id: string;
  key: string;
  url: string;
  thumbnailUrl?: string;
  duration?: number;
  size?: number;
  uploadedAt: Date;
}

class MockS3Service {
  private videos: S3Video[] = [
    {
      id: '1',
      key: 'performances/astrology-solves-all-problems-julia-shiplett.mp4',
      url: '/assets/Astrology Solves All of Your Problems - Julia Shiplett - Stand-Up Featuring.mp4',
      thumbnailUrl: '/assets/video-poster.svg',
      duration: 300, // 5 minutes (estimated)
      size: 52428800, // 50MB (estimated)
      uploadedAt: new Date('2024-01-15T10:30:00Z')
    },
    {
      id: '2', 
      key: 'performances/comedy-set-2.mp4',
      url: '/assets/mock-performance-2.mp4',
      thumbnailUrl: '/assets/video-poster-2.jpg',
      duration: 240, // 4 minutes
      size: 20971520, // 20MB
      uploadedAt: new Date('2024-01-20T14:15:00Z')
    }
  ];

  // Simulate S3 GetObject call
  async getVideo(videoId: string): Promise<S3Video | null> {
    // Simulate network delay
    await new Promise(resolve => setTimeout(resolve, 100));
    
    const video = this.videos.find(v => v.id === videoId);
    return video || null;
  }

  // Simulate S3 ListObjects call
  async listVideos(): Promise<S3Video[]> {
    // Simulate network delay
    await new Promise(resolve => setTimeout(resolve, 200));
    
    return [...this.videos];
  }

  // Simulate S3 PutObject call (for future upload functionality)
  async uploadVideo(file: File, key: string): Promise<S3Video> {
    // Simulate upload delay
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    const newVideo: S3Video = {
      id: Date.now().toString(),
      key,
      url: URL.createObjectURL(file), // For uploaded files, use blob URL
      thumbnailUrl: '/assets/video-poster.svg',
      duration: 0, // Would be calculated from video metadata
      size: file.size,
      uploadedAt: new Date()
    };
    
    this.videos.push(newVideo);
    return newVideo;
  }

  // Simulate S3 DeleteObject call
  async deleteVideo(videoId: string): Promise<boolean> {
    // Simulate network delay
    await new Promise(resolve => setTimeout(resolve, 300));
    
    const index = this.videos.findIndex(v => v.id === videoId);
    if (index !== -1) {
      this.videos.splice(index, 1);
      return true;
    }
    return false;
  }

  // Get signed URL (simulated)
  async getSignedUrl(key: string): Promise<string> {
    // In real S3, this would generate a signed URL
    // For now, just return the local path
    const video = this.videos.find(v => v.key === key);
    return video?.url || `/assets/${key.split('/').pop()}`;
  }
}

// Export singleton instance
export const s3Service = new MockS3Service();

// Real S3 service interface (for future implementation)
export interface IS3Service {
  getVideo(videoId: string): Promise<S3Video | null>;
  listVideos(): Promise<S3Video[]>;
  uploadVideo(file: File, key: string): Promise<S3Video>;
  deleteVideo(videoId: string): Promise<boolean>;
  getSignedUrl(key: string, expiresIn?: number): Promise<string>;
} 