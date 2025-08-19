import { useState } from "react";
import Profile from "./components/Profile";
import UploadPerformance from "./components/UploadPerformance";
import JokeAnalysis from "./components/JokeAnalysis";
import Settings from "./components/Settings";
import EditProfile from "./components/EditProfile";
import ThemeSettings from "./components/ThemeSettings";
import CommunityHub from "./components/CommunityHub";
import VoiceRecorder from "./components/VoiceRecorder";
import Summary from "./components/Summary";
import Groups from "./components/Groups";


function App() {
  const [view, setView] = useState("profile"); // Changed default to profile (home page)
  const [navigationParams, setNavigationParams] = useState<{ [key: string]: any }>({});

  const navigateTo = (destination: string, params?: { [key: string]: any }) => {
    setView(destination);
    if (params) {
      setNavigationParams(params);
    } else {
      setNavigationParams({});
    }
  };

  return (
    <div className="min-h-screen bg-white">
      {view === "profile" && <Profile onNavigate={navigateTo} />}
      {view === "upload" && <UploadPerformance onNavigate={navigateTo} />}
      {view === "analysis" && <JokeAnalysis onNavigate={navigateTo} videoTitle={navigationParams.videoTitle} />}
      {view === "settings" && <Settings onNavigate={navigateTo} />}
      {view === "edit-profile" && <EditProfile onNavigate={navigateTo} />}
      {view === "theme-settings" && <ThemeSettings onNavigate={navigateTo} />}
      {view === "community" && <CommunityHub onNavigate={navigateTo} />}
      {view === "groups" && <Groups onNavigate={navigateTo} />}
      {view === "voice-recorder" && <VoiceRecorder onNavigate={navigateTo} />}
      {view === "summary" && <Summary onNavigate={navigateTo} />}
    </div>
  );
}

export default App;
