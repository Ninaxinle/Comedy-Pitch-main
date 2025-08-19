// Types for analysis API
export interface Sentence {
  id: string;
  text: string;
  startTime: number;
  endTime: number;
}

export interface VideoSegment {
  id: string;
  title: string;
  startTime: number;
  endTime: number;
  duration: number;
  segmentText: string;
  score: string;
}

export interface SegmentTimestamps {
  segmentId: string;
  sentences: Sentence[];
}

export interface SegmentAnalysis {
  segmentId: string;
  feedback: {
    summary: string;
    details: Array<{
      subtype: string;
      message: string;
    }>;
  };
}

export interface VideoAnalysis {
  videoId: string;
  overallScore: string;
  performanceSummary: string;
  segments: VideoSegment[];
}

export interface VideoSummary {
  videoId: string;
  summary: string;
}

export interface FunnyScore {
  segmentId: string;
  funnyScore: number;
}

// Raw data types from JSON files
interface RawSegment {
  segment_id: number;
  sentence_indexes: number[];
  start_time: number;
  end_time: number;
  duration: number;
  text: string;
  total_gap: number;
}

interface RawSentence {
  index: number;
  text: string;
  start_time: number;
  end_time: number;
  gap_to_next: number;
}

interface RawAnalysis {
  segment_id: number;
  text: string;
  feedback: {
    summary: string;
    details: Array<{
      subtype: string;
      message: string;
    }>;
  };
}

// Mock Analysis Service
class MockAnalysisService {
  // Map video titles to their corresponding mock data
  private async getVideoDataByTitle(videoTitle: string) {
    try {
      console.log(`Loading analysis data for video: "${videoTitle}"`);
      
      // Map video titles to actual filenames (using the exact filenames from the directory)
      const titleToFilenameMap: { [key: string]: string } = {
        "Bill Burr - I'll Never Own a Helicopter - Full Special": "Bill Burr - I\u2019ll Never Own a Helicopter - Full Special",
        "Auguste White's New Revenge Personality - Stand-Up Featuring": "Auguste White\u2019s New Revenge Personality - Stand-Up Featuring",
        "Astrology Solves All of Your Problems - Julia Shiplett - Stand-Up Featuring": "Astrology Solves All of Your Problems - Julia Shiplett - Stand-Up Featuring",
        "Becoming a Corrupt Religious Leader Is Easy - Noah Gardenswartz - Stand-Up Featuring": "Becoming a Corrupt Religious Leader Is Easy - Noah Gardenswartz - Stand-Up Featuring",
        "Black Music Tells You Everything You Need to Know - Roy Wood Jr.": "Black Music Tells You Everything You Need to Know - Roy Wood Jr.",
        "Aziz Ansari - Dangerously Delicious - Texting With Girls": "Aziz Ansari - Dangerously Delicious - Texting With Girls"
      };
      
      // Get the actual filename for this video title
      const actualFilename = titleToFilenameMap[videoTitle];
      
      if (!actualFilename) {
        throw new Error(`No filename mapping found for video: ${videoTitle}`);
      }
      
      // Helper function to fetch files using the actual filename
      const fetchFile = async (suffix: string, isJson: boolean = true) => {
        const path = `${actualFilename}${suffix}`;
        
        // Try multiple approaches to handle the apostrophe issue
        const attempts = [
          `/mock-analysis-data/${encodeURIComponent(path)}`,
          `/mock-analysis-data/${path.replace(/'/g, '%27')}`,
          `/mock-analysis-data/${path.replace(/'/g, '&#39;')}`,
          `/mock-analysis-data/${path.replace(/'/g, '')}`, // Remove apostrophe entirely
          `/mock-analysis-data/${path.replace(/White's/g, 'Whites').replace(/I'll/g, 'Ill')}`, // Specific replacements
          `/mock-analysis-data/${path.replace(/'/g, '\u2019')}`, // Replace with smart apostrophe
          `/mock-analysis-data/${path}`
        ];
        
        for (const url of attempts) {
          try {
            console.log(`Trying: ${url}`);
            const response = await fetch(url);
            if (response.ok) {
              console.log(`Success with: ${url}`);
              const content = await response.text();
              console.log(`Response content preview: ${content.substring(0, 100)}`);
              if (isJson) {
                try {
                  return JSON.parse(content);
                } catch (parseError) {
                  console.error(`JSON parse error for ${url}:`, parseError);
                  console.error(`Content was: ${content.substring(0, 200)}`);
                  continue; // Try next attempt
                }
              } else {
                return content;
              }
            }
          } catch (error) {
            console.warn(`Failed with ${url}:`, error);
          }
        }
        
        throw new Error(`Failed to fetch ${path} with all attempts`);
      };
      
      // Load data from JSON files - handle missing funnyscores file gracefully
      const [segmentsData, sentencesData, analysisData, summaryData] = await Promise.all([
        fetchFile('_segments.json'),
        fetchFile('_sentences.json'),
        fetchFile('_analysis.json'),
        fetchFile('_summary.txt', false)
      ]);
      
      // Try to load funnyscores file, but don't fail if it doesn't exist
      let funnyScoresData = [];
      try {
        funnyScoresData = await fetchFile('_funnyscores.json');
      } catch (error) {
        console.warn(`No funnyscores file found for ${videoTitle}, will generate random scores`);
      }
      
      return {
        summary: summaryData,
        segments: segmentsData,
        sentences: sentencesData,
        analysis: analysisData,
        funnyScores: funnyScoresData
      };
    } catch (error) {
      console.error(`Error loading data for video: "${videoTitle}"`, error);
      console.error(`Attempted to load files:`);
      console.error(`- /mock-analysis-data/${videoTitle}_segments.json`);
      console.error(`- /mock-analysis-data/${videoTitle}_sentences.json`);
      console.error(`- /mock-analysis-data/${videoTitle}_analysis.json`);
      console.error(`- /mock-analysis-data/${videoTitle}_summary.txt`);
      return null;
    }
  }

  private mapSegmentToVideoSegment(rawSegment: RawSegment): VideoSegment {
    return {
      id: rawSegment.segment_id.toString(),
      title: `Segment ${rawSegment.segment_id}`,
      startTime: rawSegment.start_time,
      endTime: rawSegment.end_time,
      duration: rawSegment.duration,
      segmentText: rawSegment.text,
      score: this.calculateSegmentScore()
    };
  }

  private mapSentencesToSegmentTimestamps(segmentId: number, videoData: any): SegmentTimestamps {
    const rawSegment = videoData.segments.find((s: RawSegment) => s.segment_id === segmentId);
    if (!rawSegment) {
      return { segmentId: segmentId.toString(), sentences: [] };
    }

    const sentences = rawSegment.sentence_indexes.map((index: number) => {
      const rawSentence = videoData.sentences.find((s: RawSentence) => s.index === index);
      if (!rawSentence) return null;

      return {
        id: `sentence_${index}`,
        text: rawSentence.text,
        startTime: rawSentence.start_time,
        endTime: rawSentence.end_time
      };
    }).filter(Boolean) as Sentence[];

    return {
      segmentId: segmentId.toString(),
      sentences
    };
  }

  private mapAnalysisToSegmentAnalysis(rawAnalysis: RawAnalysis): SegmentAnalysis {
    // The new structure has feedback.summary and feedback.details directly
    const feedback = {
      summary: rawAnalysis.feedback.summary,
      details: rawAnalysis.feedback.details
    };

    return {
      segmentId: rawAnalysis.segment_id.toString(),
      feedback
    };
  }

  private calculateSegmentScore(): string {
    // For now, return a random score between 3-8
    const randomScore = Math.floor(Math.random() * 6) + 3; // 3 to 8
    return randomScore.toFixed(1);
  }

  async getVideoAnalysis(videoId: string, videoTitle?: string): Promise<VideoAnalysis> {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 800));
    
    console.log(`API Call: GET /api/videos/${videoId}/analysis`);

    // Get video data based on title
    const videoData = await this.getVideoDataByTitle(videoTitle || 'Astrology Solves All of Your Problems - Julia Shiplett - Stand-Up Featuring');
    
    if (!videoData) {
      throw new Error(`No mock data found for video: ${videoTitle}`);
    }

    const segments = videoData.segments.map((segment: RawSegment) => ({
      ...this.mapSegmentToVideoSegment(segment),
      score: this.calculateSegmentScore()
    }));
    
    // Calculate overall score
    const totalScore = segments.reduce((sum: number, segment: any) => sum + parseFloat(segment.score), 0);
    const overallScore = (totalScore / segments.length).toFixed(1);

    return {
      videoId,
      overallScore,
      performanceSummary: "This is a strong comedic performance that demonstrates excellent audience engagement and timing. The material shows good structure with clear setups and punchlines, while the delivery maintains consistent energy throughout. The content is relatable and well-angled, particularly the astrology theme which resonates well with the target audience.",
      segments
    };
  }

  async getVideoSummary(videoId: string, videoTitle?: string): Promise<VideoSummary> {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 500));
    console.log(`API Call: GET /api/videos/${videoId}/summary`);
    
    // Get video data based on title
    const videoData = await this.getVideoDataByTitle(videoTitle || 'Astrology Solves All of Your Problems - Julia Shiplett - Stand-Up Featuring');
    
    if (!videoData) {
      throw new Error(`No mock data found for video: ${videoTitle}`);
    }
    
    return {
      videoId,
      summary: videoData.summary
    };
  }

  async getFunnyScores(videoTitle?: string): Promise<FunnyScore[]> {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 500));
    console.log(`API Call: GET /api/videos/funny-scores`);

    // Get video data based on title
    const videoData = await this.getVideoDataByTitle(videoTitle || 'Astrology Solves All of Your Problems - Julia Shiplett - Stand-Up Featuring');

    if (!videoData) {
      throw new Error(`No mock data found for video: ${videoTitle}`);
    }

    // If funny scores exist, use them; otherwise generate random scores based on segments
    if (videoData.funnyScores && videoData.funnyScores.length > 0) {
      return videoData.funnyScores.map((fs: any) => ({
        segmentId: fs.segment_id.toString(),
        funnyScore: fs.funny_score
      }));
    } else {
      // Generate random funny scores for each segment
      return videoData.segments.map((segment: any) => ({
        segmentId: segment.segment_id.toString(),
        funnyScore: Math.floor(Math.random() * 6) // 0-5 scale
      }));
    }
  }

  async getSegmentTimestamps(segmentId: string, videoTitle?: string): Promise<SegmentTimestamps> {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 300));
    
    console.log(`API Call: GET /api/segments/${segmentId}/timestamps`);
    
    // Get video data based on title
    const videoData = await this.getVideoDataByTitle(videoTitle || 'Astrology Solves All of Your Problems - Julia Shiplett - Stand-Up Featuring');
    
    if (!videoData) {
      throw new Error(`No mock data found for video: ${videoTitle}`);
    }
    
    return this.mapSentencesToSegmentTimestamps(parseInt(segmentId), videoData);
  }

  async getSegmentAnalyses(segmentIds: string[], videoTitle?: string): Promise<SegmentAnalysis[]> {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 600));
    
    console.log(`API Call: GET /api/segments/analysis?ids=${segmentIds.join(',')}`);
    
    // Get video data based on title
    const videoData = await this.getVideoDataByTitle(videoTitle || 'Astrology Solves All of Your Problems - Julia Shiplett - Stand-Up Featuring');
    
    if (!videoData) {
      throw new Error(`No mock data found for video: ${videoTitle}`);
    }
    
    return segmentIds.map(id => {
      const rawAnalysis = videoData.analysis.find((a: RawAnalysis) => a.segment_id === parseInt(id));
      if (!rawAnalysis) {
        // Return default analysis if not found
        return {
          segmentId: id,
          feedback: {
            summary: "Analysis not available for this segment.",
            details: []
          }
        };
      }
      return this.mapAnalysisToSegmentAnalysis(rawAnalysis);
    });
  }
}

export const analysisService = new MockAnalysisService(); 