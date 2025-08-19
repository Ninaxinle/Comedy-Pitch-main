import React, { useState, useEffect, useRef } from 'react';

import { S3Video } from '../services/s3Service';
import { analysisService, VideoAnalysis, VideoSegment, SegmentAnalysis, Sentence, SegmentTimestamps, VideoSummary, FunnyScore } from '../services/analysisService';
import { PosterGenerator } from '../utils/posterGenerator';
import { 
  FiSmile, 
  FiZap, 
  FiPlay, 
  FiPause,
  FiCheck, 
  FiMessageCircle, 
  FiMenu, 
  FiChevronLeft, 
  FiZap as FiLightning
} from 'react-icons/fi';

interface JokeAnalysisProps {
  onNavigate?: (destination: string, params?: { [key: string]: any }) => void;
  videoTitle?: string;
}



const VideoPlayer = ({ video, isCompact, isFloating = false, videoRef, onPlay, onPause }: { 
  video: S3Video | null, 
  isCompact: boolean, 
  isFloating?: boolean, 
  videoRef: React.RefObject<HTMLVideoElement>,
  onPlay?: () => void,
  onPause?: () => void
}) => {
  const [isPlaying, setIsPlaying] = useState(false);

  // Add effect to monitor video state changes
  useEffect(() => {
    const videoElement = videoRef.current;
    if (!videoElement) return;

    const handlePlay = () => {
      setIsPlaying(true);
      onPlay?.();
    };
    
    const handlePause = () => {
      setIsPlaying(false);
      onPause?.();
    };

    const handleEnded = () => {
      setIsPlaying(false);
      onPause?.();
    };

    const handleTimeUpdate = () => {
      // This will help ensure we're tracking video time accurately
    };

    // Add event listeners
    videoElement.addEventListener('play', handlePlay);
    videoElement.addEventListener('pause', handlePause);
    videoElement.addEventListener('ended', handleEnded);
    videoElement.addEventListener('timeupdate', handleTimeUpdate);

    // Cleanup
    return () => {
      videoElement.removeEventListener('play', handlePlay);
      videoElement.removeEventListener('pause', handlePause);
      videoElement.removeEventListener('ended', handleEnded);
      videoElement.removeEventListener('timeupdate', handleTimeUpdate);
    };
  }, [videoRef, onPlay, onPause]);

  const handleVideoClick = (e: React.MouseEvent) => {
    console.log('Video container clicked, target:', e.target);
    
    // Don't trigger if clicking on video controls (buttons, inputs, or control bar)
    const target = e.target as HTMLElement;
    if (target.closest('input') || target.closest('video::-webkit-media-controls')) {
      console.log('Click blocked - controls detected');
      return;
    }

    // Allow clicking on the video element itself to play/pause
    if (videoRef.current) {
      console.log('Attempting to toggle play/pause, current state:', isPlaying);
      if (isPlaying) {
        videoRef.current.pause();
      } else {
        videoRef.current.play();
      }
    }
  };

  if (!video) {
    return (
      <div className={`bg-gray-100 rounded-xl overflow-hidden transition-all duration-300 flex items-center justify-center ${isCompact ? 'h-32' : 'h-64'}`}>
        <div className="text-center">
          <FiSmile className="w-12 h-12 text-gray-400 mx-auto mb-2" />
          <p className="text-gray-500 font-inter">Loading video...</p>
        </div>
      </div>
    );
  }

  const containerClasses = isFloating 
    ? `bg-black rounded-xl overflow-hidden shadow-2xl border border-gray-200 transition-all duration-300 w-full h-full cursor-pointer`
    : `bg-black rounded-xl overflow-hidden transition-all duration-300 relative cursor-pointer ${isCompact ? 'h-32' : 'h-64'}`;

  return (
    <div className={containerClasses}>
      <video 
        ref={videoRef}
        className="w-full h-full object-cover"
        poster={video.thumbnailUrl}
        onPlay={() => setIsPlaying(true)}
        onPause={() => setIsPlaying(false)}
        playsInline
        webkit-playsinline
      >
        <source src={video.url} type="video/mp4" />
        Your browser does not support the video tag.
      </video>
      
      {/* Transparent overlay for click-to-play */}
      <div 
        className="absolute inset-0 z-10 cursor-pointer"
        onClick={handleVideoClick}
        style={{ pointerEvents: 'auto' }}
      />
      
      {/* Custom play/pause button overlay */}
      <div className="absolute inset-0 z-20 flex items-center justify-center pointer-events-none">
        <button
          onClick={handleVideoClick}
          className={`w-16 h-16 rounded-full bg-black/50 backdrop-blur-sm flex items-center justify-center transition-all duration-300 pointer-events-auto ${
            isPlaying ? 'opacity-0 hover:opacity-100' : 'opacity-100'
          }`}
        >
          {isPlaying ? (
            <FiPause className="w-8 h-8 text-white" />
          ) : (
            <FiPlay className="w-8 h-8 text-white ml-1" />
          )}
        </button>
      </div>
      
      {video.duration && !isFloating && (
        <div className="absolute bottom-2 right-2 bg-black/70 text-white text-xs px-2 py-1 rounded z-20">
          {Math.floor(video.duration / 60)}:{(video.duration % 60).toString().padStart(2, '0')}
        </div>
      )}
    </div>
  );
};

const SentenceLine = ({ 
  sentence, 
  onSeek, 
  isActive 
}: { 
  sentence: Sentence; 
  onSeek: (time: number) => void;
  isActive: boolean;
}) => {
  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div 
      id={`sentence-${sentence.id}`}
      className={`p-3 rounded-lg cursor-pointer transition-all duration-200 hover:bg-blue-50 hover:border-blue-200 ${
        isActive 
          ? 'bg-blue-100 border-2 border-blue-400 shadow-md ring-2 ring-blue-200' 
          : 'bg-gray-50 border border-gray-200 hover:shadow-sm'
      }`}
      onClick={() => onSeek(sentence.startTime)}
    >
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className={`font-inter text-sm leading-relaxed ${
            isActive ? 'text-blue-900 font-medium' : 'text-gray-700'
          }`}>
            {sentence.text}
          </p>
        </div>
        <div className="ml-3 flex items-center space-x-2">
          <span className={`text-xs font-mono px-2 py-1 rounded ${
            isActive 
              ? 'text-blue-700 bg-blue-200' 
              : 'text-gray-500 bg-gray-100'
          }`}>
            {formatTime(sentence.startTime)}
          </span>
          {isActive && (
            <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
          )}
          <FiSmile 
            className={`w-4 h-4 transition-colors ${
              isActive ? 'text-blue-500' : 'text-gray-400 hover:text-blue-500'
            }`} 
          />
        </div>
      </div>
    </div>
  );
};

const SegmentCard = ({ 
  segment,
  analysis,
  onSeekToTime,
  videoTitle,
  currentSegmentId,
  setCurrentSegmentId,
  currentSentenceId,
  funnyScores,
  videoRef,
  isVideoPlaying,
  expandedSegments,

  onGlobalSentenceViewToggle,
  globalSentenceView,
  allTimestamps,
  loadingTimestamps
}: {
  segment: VideoSegment;
  analysis: SegmentAnalysis;
  onSeekToTime: (time: number) => void;
  videoTitle: string;
  currentSegmentId: string | null;
  setCurrentSegmentId: (id: string | null) => void;
  currentSentenceId: string | null;
  funnyScores: FunnyScore[];
  isSynced: boolean;
  videoRef: React.RefObject<HTMLVideoElement>;
  isVideoPlaying: boolean;
  expandedSegments: Set<string>;
  setExpandedSegments: React.Dispatch<React.SetStateAction<Set<string>>>;
  onGlobalSentenceViewToggle: () => void;
  globalSentenceView: boolean;
  allTimestamps: { [key: string]: SegmentTimestamps };
  loadingTimestamps: boolean;
}) => {
  const [timestamps, setTimestamps] = useState<SegmentTimestamps | null>(null);

  const [showFullText, setShowFullText] = useState(false);

  // Check if this segment is expanded
  const isExpanded = expandedSegments.has(segment.id);
  
  // Get timestamps from global state or local state
  const segmentTimestamps = allTimestamps[segment.id] || timestamps;
  const isGlobalLoading = loadingTimestamps && !allTimestamps[segment.id];

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  // Get funny score for this segment
  const funnyScore = funnyScores && Array.isArray(funnyScores) && funnyScores.length > 0 
    ? funnyScores.find(fs => fs.segmentId === segment.id)?.funnyScore || 0
    : 0;

  // Get emoji for funny score
  const getFunnyEmoji = (score: number) => {
    switch (score) {
      case 0: return '😐';
      case 1: return '😕';
      case 2: return '😐';
      case 3: return '😊';
      case 4: return '😄';
      case 5: return '🤣';
      default: return '😐';
    }
  };

  // Format subtype: remove underscores and capitalize first letter of each word
  const formatSubtype = (subtype: string) => {
    return subtype
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  const handleExpandClick = async () => {
    // Use global sentence view toggle instead of individual segment expansion
    onGlobalSentenceViewToggle();
    
    // Load timestamps for this segment if not already loaded (for individual segment expansion)
    if (!timestamps && !globalSentenceView) {
              // Loading handled by parent
      try {
        const timestampData = await analysisService.getSegmentTimestamps(segment.id, videoTitle);
        setTimestamps(timestampData);
      } catch (error) {
        console.error('Failed to load timestamps:', error);
      } finally {
        // Loading handled by parent
      }
    }
  };

  const handleTextClick = () => {
    setShowFullText(!showFullText);
  };

  return (
    <div 
      id={`segment-${segment.id}`}
      className={`bg-white rounded-xl p-6 border border-gray-200 shadow-sm transition-all duration-300 ${
        currentSegmentId === segment.id && isVideoPlaying
          ? 'ring-2 ring-blue-500 ring-opacity-50 bg-blue-50 border-blue-300'
          : currentSegmentId === segment.id
          ? 'ring-1 ring-blue-300 border-blue-200'
          : ''
      }`}
    >
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-3">
          <FiZap className="w-6 h-6 text-gray-600" />
          <h3 className="font-display text-lg font-semibold text-gray-900">{segment.title}</h3>
          {currentSegmentId === segment.id && isVideoPlaying ? (
            <button
              onClick={() => {
                if (videoRef.current) {
                  videoRef.current.pause();
                }
                setCurrentSegmentId(null);
              }}
              className="flex items-center space-x-1 px-2 py-1 rounded-lg bg-blue-100 hover:bg-blue-200 transition-colors cursor-pointer"
            >
              <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
              <span className="text-xs text-blue-600 font-medium">Now Playing</span>
            </button>
          ) : (
            <button
              onClick={() => onSeekToTime(segment.startTime)}
              className="flex items-center space-x-1 px-2 py-1 rounded-lg bg-gray-100 hover:bg-gray-200 transition-colors cursor-pointer"
            >
              <FiPlay className="w-3 h-3 text-gray-500" />
              <span className="text-xs text-gray-600 font-medium">Play</span>
            </button>
          )}
        </div>
        <div className="flex items-center space-x-2">
          <div className="flex items-center space-x-2">
            <span className="text-2xl">{getFunnyEmoji(funnyScore)}</span>
            <span className="text-sm font-medium text-gray-600">{funnyScore}/5</span>
          </div>
        </div>
      </div>

      <div className="space-y-6">
        {/* Segment Text - Preview or Interactive Sentences */}
        <div>
          <div className="flex items-center space-x-2 mb-3">
            <FiMessageCircle className="w-5 h-5 text-gray-500" />
            <span className="font-inter text-sm font-semibold text-gray-600">Segment Text</span>
          </div>
          
          <div className="flex items-center justify-between mb-3">
            <div className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">
              {formatTime(segment.startTime)} - {formatTime(segment.endTime)} ({formatTime(segment.duration)})
            </div>
            <button
              onClick={handleExpandClick}
              className="text-xs text-blue-600 hover:text-blue-700 font-medium px-2 py-1 rounded hover:bg-blue-50 transition-colors"
            >
              {globalSentenceView ? 'Collapse All' : 'Sentence View'}
            </button>
          </div>

          {!isExpanded ? (
            // Preview mode - show truncated text
            <div 
              className="bg-gray-50 rounded-lg border border-gray-200 p-4 cursor-pointer hover:bg-gray-100 transition-colors relative"
              onClick={handleTextClick}
            >
              <p className={`font-inter text-sm text-gray-700 leading-relaxed italic ${
                !showFullText && segment.segmentText.length > 200 ? 'line-clamp-4' : ''
              }`}>
                "{segment.segmentText}"
              </p>
            </div>
          ) : (
            // Interactive mode - show sentences with timestamps
            <div>
              {isGlobalLoading ? (
                <div className="text-center py-4">
                  <FiSmile className="w-8 h-8 text-gray-400 mx-auto mb-2" />
                  <p className="text-gray-500 font-inter text-sm">Loading timestamps...</p>
                </div>
              ) : segmentTimestamps ? (
                <div className="space-y-2 max-h-64 overflow-y-auto scrollbar-thin scrollbar-thumb-gray-300 scrollbar-track-gray-100">
                  {segmentTimestamps.sentences.map((sentence) => (
                    <SentenceLine 
                      key={sentence.id}
                      sentence={sentence}
                      onSeek={onSeekToTime}
                      isActive={currentSentenceId === sentence.id}
                    />
                  ))}
                </div>
              ) : (
                <div className="text-center py-4 text-red-500">
                  Failed to load timestamps
                </div>
              )}
            </div>
          )}
        </div>

        {/* Feedback */}
                  <div>
            <div className="flex items-center space-x-2 mb-4">
              <FiMessageCircle className="w-5 h-5 text-gray-500" />
              <span className="font-inter text-sm font-semibold text-gray-600">Feedback</span>
            </div>
          
          {/* Feedback Summary */}
          <div className="mb-4 p-3 bg-blue-50 rounded-lg border border-blue-200">
            <p className="font-inter text-sm text-blue-800 italic">"{analysis.feedback.summary}"</p>
          </div>
          
          {/* Detailed Feedback */}
          {analysis.feedback.details.length > 0 && (
            <div className="space-y-3">
              {analysis.feedback.details.map((detail, index) => (
                <div key={index} className="p-3 bg-gray-50 rounded-lg border border-gray-200">
                  <p className="font-inter text-sm text-gray-700 leading-relaxed">
                    <span className="font-semibold text-blue-700">{formatSubtype(detail.subtype)}: </span>
                    {detail.message}
                  </p>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default function JokeAnalysis({ onNavigate, videoTitle: propVideoTitle }: JokeAnalysisProps) {
  const [isVideoCompact, setIsVideoCompact] = useState(false);
  const [isVideoFloating, setIsVideoFloating] = useState(false);
  const [video, setVideo] = useState<S3Video | null>(null);
  const [videoAnalysis, setVideoAnalysis] = useState<VideoAnalysis | null>(null);
  const [videoSummary, setVideoSummary] = useState<VideoSummary | null>(null);
  const [segmentAnalyses, setSegmentAnalyses] = useState<{ [key: string]: SegmentAnalysis }>({});
  const [loading, setLoading] = useState(true);
  const [loadingSegments, setLoadingSegments] = useState(false);
  const [videoTitle] = useState(propVideoTitle || 'Astrology Solves All of Your Problems - Julia Shiplett - Stand-Up Featuring');
  const [isSummaryExpanded, setIsSummaryExpanded] = useState(false);
  const [isSynced, setIsSynced] = useState(false);
  const [currentSegmentId, setCurrentSegmentId] = useState<string | null>(null);
  const [currentSentenceId, setCurrentSentenceId] = useState<string | null>(null);
  const [funnyScores, setFunnyScores] = useState<FunnyScore[]>([]);
  const [isVideoPlaying, setIsVideoPlaying] = useState(false);
  const [allSentences, setAllSentences] = useState<Sentence[]>([]);
  const [expandedSegments, setExpandedSegments] = useState<Set<string>>(new Set());
  const [globalSentenceView, setGlobalSentenceView] = useState(false);
  const [allTimestamps, setAllTimestamps] = useState<{ [key: string]: SegmentTimestamps }>({});
  const [loadingTimestamps, setLoadingTimestamps] = useState(false);
  const [isHeaderVisible, setIsHeaderVisible] = useState(true);
  const [lastScrollY, setLastScrollY] = useState(0);
  const videoRef = useRef<HTMLVideoElement>(null);

  // Calculate overall funny score based on weighted average of segment scores
  const calculateOverallFunnyScore = (): number => {
    if (!videoAnalysis || !funnyScores || funnyScores.length === 0) {
      return 0;
    }

    let totalWeightedScore = 0;
    let totalDuration = 0;

    // Calculate weighted score based on segment duration
    for (const segment of videoAnalysis.segments) {
      const segmentFunnyScore = funnyScores.find(fs => fs.segmentId === segment.id)?.funnyScore || 0;
      const segmentDuration = segment.duration;
      
      totalWeightedScore += segmentFunnyScore * segmentDuration;
      totalDuration += segmentDuration;
    }

    // Return weighted average, rounded to 1 decimal place
    return totalDuration > 0 ? Math.round((totalWeightedScore / totalDuration) * 10) / 10 : 0;
  };

  // Get emoji for overall funny score
  const getOverallFunnyEmoji = (score: number) => {
    switch (Math.floor(score)) {
      case 0: return '😐';
      case 1: return '😕';
      case 2: return '😐';
      case 3: return '😊';
      case 4: return '😄';
      case 5: return '🤣';
      default: return '😐';
    }
  };

  // Get description for overall funny score
  const getOverallFunnyDescription = (score: number): string => {
    if (score >= 4.5) return "Absolutely hilarious! A masterclass in comedy.";
    if (score >= 4.0) return "Very funny! Strong performance with great laughs.";
    if (score >= 3.5) return "Quite funny! Good material and delivery.";
    if (score >= 3.0) return "Moderately funny! Solid performance.";
    if (score >= 2.5) return "Somewhat funny! Room for improvement.";
    if (score >= 2.0) return "A bit funny! Needs more punchlines.";
    if (score >= 1.5) return "Slightly funny! Consider revising material.";
    if (score >= 1.0) return "Not very funny! Major improvements needed.";
    return "Not funny! Complete rewrite recommended.";
  };

  // Handle seeking to specific time in video
  const handleSeekToTime = (time: number) => {
    if (videoRef.current) {
      videoRef.current.currentTime = time;
      videoRef.current.play();
      
      // Find and set the current segment when manually seeking
      if (videoAnalysis) {
        const targetSegment = videoAnalysis.segments.find(segment => 
          time >= segment.startTime && time < segment.endTime
        );
        if (targetSegment) {
          setCurrentSegmentId(targetSegment.id);
          // Don't automatically enable sync when manually seeking
        }
      }
    }
  };

  // Handle sync with video
  const handleSyncToggle = () => {
    setIsSynced(!isSynced);
  };

  // Handle global sentence view toggle
  const handleGlobalSentenceViewToggle = () => {
    if (!globalSentenceView) {
      // Expand all segments to sentence view
      const allSegmentIds = videoAnalysis?.segments.map(segment => segment.id) || [];
      setExpandedSegments(new Set(allSegmentIds));
      setGlobalSentenceView(true);
      
      // Load timestamps for all segments in parallel
      const loadAllTimestamps = async () => {
        setLoadingTimestamps(true);
        const timestampPromises = allSegmentIds.map(async (segmentId) => {
          try {
            const timestampData = await analysisService.getSegmentTimestamps(segmentId, videoTitle);
            return { segmentId, timestampData };
          } catch (error) {
            console.error(`Failed to load timestamps for segment ${segmentId}:`, error);
            return { segmentId, timestampData: null };
          }
        });
        
        const results = await Promise.all(timestampPromises);
        const timestampsMap: { [key: string]: SegmentTimestamps } = {};
        
        results.forEach(({ segmentId, timestampData }) => {
          if (timestampData) {
            timestampsMap[segmentId] = timestampData;
          }
        });
        
        setAllTimestamps(timestampsMap);
        setLoadingTimestamps(false);
      };
      
      loadAllTimestamps();
    } else {
      // Collapse all segments
      setExpandedSegments(new Set());
      setGlobalSentenceView(false);
    }
  };

  // Track current segment based on video time
  useEffect(() => {
    if (!videoAnalysis || !videoRef.current) return;

    const updateCurrentSegment = () => {
      const currentTime = videoRef.current?.currentTime || 0;
      
      // Find the segment that contains the current time
      const currentSegment = videoAnalysis.segments.find(segment => 
        currentTime >= segment.startTime && currentTime < segment.endTime
      );
      
      if (currentSegment) {
        // Only update if the segment has actually changed
        if (currentSegmentId !== currentSegment.id) {
          setCurrentSegmentId(currentSegment.id);
          // Don't auto-expand segments - let user control sentence view state
        }
      } else {
        setCurrentSegmentId(null);
      }
    };

    // Track current sentence based on video time
    const updateCurrentSentence = () => {
      const currentTime = videoRef.current?.currentTime || 0;
      
      // Find the sentence that contains the current time
      const currentSentence = allSentences.find(sentence => 
        currentTime >= sentence.startTime && currentTime < sentence.endTime
      );
      
      if (currentSentence) {
        // Only update if the sentence has actually changed
        if (currentSentenceId !== currentSentence.id) {
          setCurrentSentenceId(currentSentence.id);
        }
      } else {
        setCurrentSentenceId(null);
      }
    };

    // Update more frequently for better responsiveness
    const interval = setInterval(() => {
      updateCurrentSegment();
      updateCurrentSentence();
    }, 250);

    return () => clearInterval(interval);
  }, [videoAnalysis, allSentences]);

  // Scroll to current sentence when it changes (only if auto-scroll is enabled)
  useEffect(() => {
    if (currentSentenceId && isSynced) {
      const element = document.getElementById(`sentence-${currentSentenceId}`);
      if (element) {
        element.scrollIntoView({ 
          behavior: 'smooth', 
          block: 'center' 
        });
      }
    }
  }, [currentSentenceId, isSynced]);

  // Scroll to current segment when it changes (only if auto-scroll is enabled)
  useEffect(() => {
    if (currentSegmentId && isSynced) {
      const element = document.getElementById(`segment-${currentSegmentId}`);
      if (element) {
        element.scrollIntoView({ 
          behavior: 'smooth', 
          block: 'center' 
        });
      }
    }
  }, [currentSegmentId, isSynced]);

  // Load video and analysis data
  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        
        // Map video title to the correct video file
        const getVideoByTitle = (title: string): S3Video | null => {
          const videoFiles = [
            "Becoming a Corrupt Religious Leader Is Easy - Noah Gardenswartz - Stand-Up Featuring.mp4",
            "Black Music Tells You Everything You Need to Know - Roy Wood Jr..mp4",
            "Astrology Solves All of Your Problems - Julia Shiplett - Stand-Up Featuring.mp4",
            "Bill Burr - I'll Never Own a Helicopter - Full Special.mp4",
            "Aziz Ansari - Dangerously Delicious - Texting With Girls.mp4",
            "Auguste White's New Revenge Personality - Stand-Up Featuring.mp4"
          ];
          
          // Find the matching video file
          const matchingFile = videoFiles.find(file => {
            // Extract title from filename (same logic as videoService)
            const nameWithoutExt = file.replace(/\.(mp4|avi|mov|mkv)$/i, '');
            let extractedTitle = nameWithoutExt.replace(/\\"/g, '"');
            extractedTitle = extractedTitle.replace(/_/g, ' ');
            extractedTitle = extractedTitle.replace(/:/g, '：');
            extractedTitle = extractedTitle.replace(/[""]/g, '"');
            
            return extractedTitle === title;
          });
          
          if (matchingFile) {
            return {
              id: '1',
              key: `performances/${matchingFile}`,
              url: `/assets/${matchingFile}`,
              thumbnailUrl: '/assets/video-poster.svg', // Will be overridden with custom poster
              duration: Math.floor(Math.random() * 900) + 300, // Random duration 5-20 minutes
              size: 52428800, // 50MB (estimated)
              uploadedAt: new Date('2024-01-15T10:30:00Z')
            };
          }
          
          return null;
        };
        
        // Get the correct video data based on title
        const videoData = getVideoByTitle(videoTitle || '');
        
        // Load analysis and summary in parallel
        const [analysisData, summaryData, funnyScoresData] = await Promise.all([
          analysisService.getVideoAnalysis('1', videoTitle),
          analysisService.getVideoSummary('1', videoTitle),
          analysisService.getFunnyScores(videoTitle)
        ]);
        
        // Set video data
        setVideo(videoData);
        
        // Generate custom poster for this video
        if (videoData && videoTitle) {
          const customPoster = PosterGenerator.generatePosterDataURL({
            title: videoTitle,
            score: analysisData?.overallScore ? parseFloat(analysisData.overallScore) : undefined,
            duration: videoData.duration,
            isPublic: true // Default to public for analysis view
          });
          
          // Update video data with custom poster
          const videoWithCustomPoster = {
            ...videoData,
            thumbnailUrl: customPoster
          };
          
          setVideo(videoWithCustomPoster);
        }
        setVideoAnalysis(analysisData);
        setVideoSummary(summaryData);
        setFunnyScores(funnyScoresData);
        
        // Load segment analyses in parallel
        setLoadingSegments(true);
        const segmentIds = analysisData.segments.map(segment => segment.id);
        const analyses = await analysisService.getSegmentAnalyses(segmentIds, videoTitle);
        
        const analysesMap = analyses.reduce((acc, analysis) => {
          acc[analysis.segmentId] = analysis;
          return acc;
        }, {} as { [key: string]: SegmentAnalysis });
        
        setSegmentAnalyses(analysesMap);
        setLoadingSegments(false);
        
        // Load all sentences from all segments for transcript highlighting
        const allSentencesData: Sentence[] = [];
        for (const segment of analysisData.segments) {
          const timestamps = await analysisService.getSegmentTimestamps(segment.id, videoTitle);
          allSentencesData.push(...timestamps.sentences);
        }
        setAllSentences(allSentencesData);
        
      } catch (error) {
        console.error('Failed to load data:', error);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [videoTitle]);

  // Handle scroll to make video compact and floating, and control header visibility
  useEffect(() => {
    const handleScroll = () => {
      const currentScrollY = window.scrollY;
      
      // Video behavior
      setIsVideoCompact(currentScrollY > 100);
      setIsVideoFloating(currentScrollY > 200);
      
      // Header visibility - show when scrolling up, hide when scrolling down
      if (currentScrollY > lastScrollY && currentScrollY > 100) {
        // Scrolling down and not at the top
        setIsHeaderVisible(false);
      } else {
        // Scrolling up or at the top
        setIsHeaderVisible(true);
      }
      
      setLastScrollY(currentScrollY);
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, [lastScrollY]);

  // Calculate floating video dimensions
  const originalHeight = 256;
  const floatingHeight = (originalHeight * 0.5) * 0.9;
  const floatingWidth = (floatingHeight * 16) / 9;

  if (loading) {
    return (
      <div className="bg-white min-h-screen flex items-center justify-center">
        <div className="text-center">
          <FiSmile className="w-16 h-16 text-gray-400 mx-auto mb-4 animate-pulse" />
          <p className="text-gray-600 font-inter animate-pulse">Loading analysis...</p>
        </div>
      </div>
    );
  }

  if (!videoAnalysis) {
    return (
      <div className="bg-white min-h-screen flex items-center justify-center">
        <div className="text-center">
          <FiLightning className="w-16 h-16 text-red-400 mx-auto mb-4 animate-pulse" />
          <p className="text-gray-600 font-inter animate-pulse">Failed to load analysis</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white min-h-screen flex flex-col">
      {/* Custom Header with scroll behavior */}
      <div className="sticky top-0 z-50">
        <header 
          className={`bg-gradient-to-br from-gray-800 via-gray-900 to-black backdrop-blur-sm border-b border-gray-700 relative overflow-hidden transition-transform duration-300 ${
            isHeaderVisible ? 'translate-y-0' : '-translate-y-full'
          }`}
        >
          {/* Red Spotlight Effect */}
          <div className="absolute top-0 left-1/2 transform -translate-x-1/2 w-40 h-40 bg-gradient-to-b from-red-500/30 to-transparent rounded-full blur-xl"></div>
          
          <div className="container mx-auto px-4 py-8 flex items-center justify-between relative z-10">
            <button 
              onClick={() => onNavigate?.('profile')}
              className="text-gray-400 hover:text-white transition-colors p-2 rounded-lg hover:bg-gray-800"
            >
              <FiChevronLeft className="h-6 w-6" />
            </button>
            <h1 className="font-display text-xl font-semibold text-white">
              Joke Analysis
            </h1>
            <div className="flex items-center space-x-2">
              <button
                onClick={handleSyncToggle}
                className={`flex items-center space-x-2 px-3 py-2 rounded-lg transition-colors ${
                  isSynced 
                    ? 'bg-green-600 text-white hover:bg-green-700' 
                    : 'text-gray-400 hover:text-white hover:bg-gray-800'
                }`}
              >
                <FiCheck className="w-4 h-4" />
                <span className="text-sm font-medium">
                  {isSynced ? 'Auto Scroll' : 'Auto Scroll'}
                </span>
              </button>
              <button className="text-gray-400 hover:text-white transition-colors p-2 rounded-lg hover:bg-gray-800">
                <FiMenu className="h-6 w-6" />
              </button>
            </div>
          </div>
        </header>
      </div>

      {/* Single Video Player - Moves between positions */}
      <div 
        className={`transition-all duration-500 ease-in-out ${
          isVideoFloating 
            ? 'fixed bottom-20 right-4 z-40' 
            : 'relative p-4'
        }`}
        style={isVideoFloating ? {
          width: `${floatingWidth}px`,
          height: `${floatingHeight}px`
        } : {}}
      >
        <VideoPlayer 
          video={video} 
          isCompact={isVideoCompact} 
          isFloating={isVideoFloating} 
          videoRef={videoRef}
          onPlay={() => setIsVideoPlaying(true)}
          onPause={() => setIsVideoPlaying(false)}
        />
      </div>

      {/* Main Content */}
      <main className="flex-grow overflow-y-auto space-y-6 pb-24">
        {/* Overall Score */}
        <div className="px-4">
          <div className="bg-gradient-to-br from-yellow-400 to-yellow-500 rounded-2xl p-6 text-center shadow-lg border border-yellow-300">
            <div className="space-y-4">
              <div className="text-center">
                <h2 className="font-display text-lg font-bold text-gray-900 mb-2">Predicted Overall Funny Score</h2>
                <div className="flex items-center justify-center space-x-3">
                  <span className="text-4xl">{getOverallFunnyEmoji(calculateOverallFunnyScore())}</span>
                  <div className="text-4xl font-bold text-gray-900">{calculateOverallFunnyScore()}/5</div>
                </div>
              </div>
              <div className="text-center max-w-xl mx-auto">
                <p className="font-inter text-sm text-gray-800 leading-relaxed font-medium">
                  {getOverallFunnyDescription(calculateOverallFunnyScore())}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Performance Summary */}
        <div className="px-4">
          <div className="bg-white rounded-xl p-6 border border-gray-200 shadow-sm">
            <h3 className="font-display text-lg font-semibold text-gray-900 mb-4">Full Performance Summary</h3>
            <div>
              <p className={`font-inter text-sm text-gray-700 leading-relaxed ${
                !isSummaryExpanded ? 'line-clamp-3' : ''
              }`}>
                {videoSummary?.summary || videoAnalysis?.performanceSummary || "Loading summary..."}
              </p>
              <button
                onClick={() => setIsSummaryExpanded(!isSummaryExpanded)}
                className="mt-3 text-blue-600 hover:text-blue-700 font-medium text-sm transition-colors"
              >
                {isSummaryExpanded ? 'View Less' : 'View More'}
              </button>
            </div>
          </div>
        </div>

        {/* Publish Question */}
        <div className="px-4">
          <div className="flex items-center justify-between bg-white rounded-xl p-4 border border-gray-200">
            <span className="font-inter text-lg font-semibold text-gray-900">Do you want to publish?</span>
            <span className="bg-blue-600 text-white text-sm font-medium px-3 py-1 rounded-full">Private</span>
          </div>
        </div>

        {/* Segments */}
        <div className="px-4 space-y-6">
          {loadingSegments ? (
            <div className="text-center py-8">
              <FiSmile className="w-12 h-12 text-gray-400 mx-auto mb-2" />
              <p className="text-gray-500 font-inter">Loading segment analysis...</p>
            </div>
          ) : (
            videoAnalysis.segments.map((segment) => {
              const analysis = segmentAnalyses[segment.id];
              if (!analysis) return null;
              
              return (
                <SegmentCard 
                  key={segment.id} 
                  segment={segment}
                  analysis={analysis}
                  onSeekToTime={handleSeekToTime}
                  videoTitle={videoTitle}
                  currentSegmentId={currentSegmentId}
                  setCurrentSegmentId={setCurrentSegmentId}
                  currentSentenceId={currentSentenceId}
                  funnyScores={funnyScores}
                  isSynced={isSynced}
                  videoRef={videoRef}
                  isVideoPlaying={isVideoPlaying}
                  expandedSegments={expandedSegments}
                  setExpandedSegments={setExpandedSegments}
                  onGlobalSentenceViewToggle={handleGlobalSentenceViewToggle}
                  globalSentenceView={globalSentenceView}
                  allTimestamps={allTimestamps}
                  loadingTimestamps={loadingTimestamps}
                />
              );
            })
          )}
        </div>
      </main>

      {/* Bottom Navigation - Hidden in analysis page for cleaner experience */}
    </div>
  );
} 