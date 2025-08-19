import { useState, useEffect } from 'react';
import { BottomNav } from './upload/BottomNav';
import { Header } from './Header';
import { videoService, Video } from '../services/videoService';
import { 
  FiUser, 
 
 
  FiEye, 
  FiEyeOff,
  FiHeart, 
  FiCalendar,
  FiPlus,
  FiVideo,
  FiSmile,
  FiCheck,

  FiZap
} from 'react-icons/fi';
import { 
  FaTwitter, 
  FaInstagram, 
  FaYoutube 
} from 'react-icons/fa';

interface ProfileProps {
  onNavigate?: (destination: string, params?: { [key: string]: any }) => void;
}

const VideoCard = ({ 
  video
}: { 
  video: Video;
}) => {
  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const formatUploadDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now.getTime() - date.getTime());
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays === 1) return '1 day ago';
    if (diffDays < 7) return `${diffDays} days ago`;
    if (diffDays < 30) return `${Math.floor(diffDays / 7)} weeks ago`;
    return `${Math.floor(diffDays / 30)} months ago`;
  };

  return (
    <div className="bg-white rounded-xl border border-gray-200 shadow-sm hover:shadow-md transition-shadow cursor-pointer">
      <div className="relative">
        <img 
          src={video.thumbnail} 
          alt={video.title}
          className="w-full h-32 object-cover rounded-t-xl"
        />
                 <div className="absolute top-2 right-2 bg-white/90 backdrop-blur-sm rounded-lg px-2 py-1">
           <div className="flex items-center space-x-1">
             <FiZap className="w-3 h-3 text-red-500" />
             <span className="text-xs font-medium text-gray-700">{video.overallScore}</span>
           </div>
         </div>
        <div className="absolute bottom-2 left-2 bg-black/70 text-white text-xs px-2 py-1 rounded">
          {formatDuration(video.duration)}
        </div>
                 <div className={`absolute top-2 left-2 text-white text-xs px-2 py-1 rounded flex items-center space-x-1 ${
           video.isPublic ? 'bg-green-600' : 'bg-gray-800'
         }`}>
                       {video.isPublic ? (
              <FiCheck className="w-3 h-3" />
            ) : (
              <FiEyeOff className="w-3 h-3" />
            )}
           <span>{video.isPublic ? 'Public' : 'Private'}</span>
         </div>
      </div>
      <div className="p-4">
        <h3 className="font-inter text-sm font-medium text-gray-900 line-clamp-2 mb-3">{video.title}</h3>
        
        {/* Upload date */}
        <div className="flex items-center space-x-1 mb-3">
          <FiCalendar className="w-3 h-3 text-gray-400" />
          <span className="text-xs text-gray-500">{formatUploadDate(video.uploadDate)}</span>
        </div>
        
        {/* Stats row with icons */}
        <div className="flex items-center space-x-4">
          {/* Views */}
          <div className="flex items-center space-x-1">
            <FiEye className="w-3 h-3 text-gray-400" />
            <span className="text-xs text-gray-500">{video.views.toLocaleString()}</span>
          </div>
          
          {/* Likes */}
          <div className="flex items-center space-x-1">
            <FiHeart className="w-3 h-3 text-gray-400" />
            <span className="text-xs text-gray-500">{video.likes}</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default function Profile({ onNavigate }: ProfileProps) {
  const [userVideos, setUserVideos] = useState<Video[]>([]);
  const [loading, setLoading] = useState(true);

  // Generate random comedian name
  const randomNames = [
    "Sarah Johnson", "Mike Rodriguez", "Alex Chen", "Emma Thompson", 
    "David Kim", "Lisa Patel", "James Wilson", "Maria Garcia",
    "Ryan O'Connor", "Jennifer Lee", "Marcus Williams", "Amanda Foster",
    "Kevin Zhang", "Rachel Green", "Tom Anderson", "Nina Singh"
  ];
  const randomName = randomNames[Math.floor(Math.random() * randomNames.length)];

  useEffect(() => {
    const loadVideos = async () => {
      try {
        setLoading(true);
        const videos = await videoService.getUserVideos();
        setUserVideos(videos);
        

      } catch (error) {
        console.error('Error loading videos:', error);
      } finally {
        setLoading(false);
      }
    };

    loadVideos();
  }, []);



  return (
    <div className="bg-white min-h-screen flex flex-col">
      <Header title="Profile" onNavigate={onNavigate!} />

      {/* Main Content */}
      <main className="flex-grow overflow-y-auto p-4 space-y-6 pb-24">
        {/* Profile Info Section */}
        <div className="bg-white rounded-xl p-6 border border-gray-200 shadow-sm">
          <div className="flex items-center space-x-4 mb-6">
            {/* Profile Photo */}
            <div className="w-20 h-20 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-full flex items-center justify-center overflow-hidden">
              <img 
                src="/assets/9decd998351cfde9c45fc40451723b54283aa78c.png" 
                alt="Profile"
                className="w-full h-full object-cover"
                onError={(e) => {
                  // Fallback to icon if image fails to load
                  e.currentTarget.style.display = 'none';
                  e.currentTarget.nextElementSibling?.classList.remove('hidden');
                }}
              />
              <FiUser className="w-10 h-10 text-white hidden" />
            </div>
                         <div className="flex-1">
               <h2 className="font-display text-xl font-semibold text-gray-900">{randomName}</h2>
               <p className="font-inter text-sm text-gray-600 mb-2">Comedian</p>
             </div>
            <button 
              onClick={() => onNavigate?.('edit-profile')}
              className="bg-gray-800 text-white px-4 py-2 rounded-lg hover:bg-gray-900 transition-colors font-inter text-sm font-medium"
            >
              Edit Profile
            </button>
          </div>
          
          <p className="font-inter text-sm text-gray-700 leading-relaxed mb-4">
            Explore the world of comedy shows! Discover performances that bring laughter and joy. 
            Passionate about creating content that makes people laugh and think.
          </p>

          {/* Social Icons */}
          <div className="flex items-center space-x-3 mb-4">
            <button className="w-10 h-10 bg-gray-100 hover:bg-gray-200 transition-colors rounded-full flex items-center justify-center">
              <FaTwitter className="w-5 h-5 text-gray-600" />
            </button>
            <button className="w-10 h-10 bg-gray-100 hover:bg-gray-200 transition-colors rounded-full flex items-center justify-center">
              <FaInstagram className="w-5 h-5 text-gray-600" />
            </button>
            <button className="w-10 h-10 bg-gray-100 hover:bg-gray-200 transition-colors rounded-full flex items-center justify-center">
              <FaYoutube className="w-5 h-5 text-gray-600" />
            </button>
          </div>

                     {/* Score Box */}
           <div className="bg-gray-50 rounded-lg p-3 inline-block">
             <div className="flex items-center space-x-2">
               <FiZap className="w-4 h-4 text-red-500" />
               <span className="font-inter text-sm font-medium text-gray-700">
                 Average Score: {userVideos.length > 0 ? (userVideos.reduce((sum, v) => sum + v.overallScore, 0) / userVideos.length).toFixed(1) : '0'}/5
               </span>
             </div>
           </div>
        </div>

        

        {/* Videos Section */}
        <div>
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-display text-lg font-semibold text-gray-900">My Performances</h3>
            <button 
              onClick={() => onNavigate?.('upload')}
              className="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition-colors font-inter text-sm font-medium flex items-center space-x-2"
            >
              <FiPlus className="w-4 h-4" />
              <span>Upload New</span>
            </button>
          </div>
          
          {loading ? (
            <div className="text-center py-8">
              <FiSmile className="w-12 h-12 text-gray-400 mx-auto mb-2" />
                             <p className="text-gray-500 font-inter">Loading performances...</p>
            </div>
                     ) : userVideos.length === 0 ? (
             <div className="text-center py-8">
               <FiVideo className="w-12 h-12 text-gray-400 mx-auto mb-2" />
               <p className="text-gray-500 font-inter">No performances uploaded yet</p>
                              <button 
                  onClick={() => onNavigate?.('upload')}
                  className="mt-4 bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition-colors font-inter text-sm font-medium"
                >
                  Upload Your First Performance
                </button>
             </div>
          ) : (
                         <div className="grid grid-cols-2 gap-4">
               {userVideos.map((video) => (
                 <div 
                   key={video.id}
                   onClick={() => onNavigate?.('analysis', { videoTitle: video.title })}
                   className="cursor-pointer"
                 >
                   <VideoCard video={video} />
                 </div>
               ))}
             </div>
          )}
        </div>
      </main>

      {/* Bottom Navigation */}
      <BottomNav onNavigate={onNavigate} currentView="profile" />
    </div>
  );
}