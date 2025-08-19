import React from 'react';
import { Header } from './Header';
import { BottomNav } from './upload/BottomNav';

// Asset imports - updating to use localhost:5173 for consistency
const imgEllipse18 = "http://localhost:5173/assets/e44311340ac1e0949a7dc5a16a29215eb351b09a.png";
const imgEllipse16 = "http://localhost:5173/assets/1b2b785fddbd89a9de7e211b6f3f28343ef3be3d.png";
const imgEllipse17 = "http://localhost:5173/assets/074bfc32f0cdea1ff16f91378c6c76a75fb1daaa.png";
const imgEllipse19 = "http://localhost:5173/assets/a0242aa10ff8627c08b4afc58bb7ee09c06f15fe.png";
const imgEllipse14 = "http://localhost:5173/assets/893052948c1e17ecf2dd97b3e25deca5db45ea35.png";
const imgEllipse20 = "http://localhost:5173/assets/6e75f9687ba66185f42e65968e544ac9bdf1f2bf.png";
const imgEllipse21 = "http://localhost:5173/assets/ca90353b5aa22b9bda39e70aa1bdd00289c5de69.png";
const imgEllipse22 = "http://localhost:5173/assets/95edfafd7a2020a40841f0c2e34cde7715ffa7ae.png";
const imgEllipse23 = "http://localhost:5173/assets/ef1d9e566074b96581501e173f1223b0d8ec861a.png";
const imgEllipse24 = "http://localhost:5173/assets/d72367fcd72231ee7501f43bf9b492e3b7c5b65e.png";
const imgEllipse15 = "http://localhost:5173/assets/539dc805e22fe5d0f85b616936a7032c3b153d5b.svg";
const imgPlus = "http://localhost:5173/assets/8ab534e9f57a1c887a17cf2931d604a093ca8f00.svg";
const imgFrame2609129 = "http://localhost:5173/assets/22bcb0942c8a275f47f71af13f0c438dc4d281e0.svg";
const imgFrame2609130 = "http://localhost:5173/assets/dcac4b6c7fb9ee7e96f505545c3a990dae7a4b89.svg";
const imgVector5 = "http://localhost:5173/assets/bd75fbc2db58ea1fa15e7eed285f672e0b5c4aae.svg";

interface GroupsProps {
  onNavigate: (view: string) => void;
}

interface ScrollPageProps {
  property1?: "Frame 2609131" | "Frame 2609133" | "writing" | "beginner";
}

function ScrollPage({ property1 = "beginner" }: ScrollPageProps) {
  return (
    <div className="relative w-full h-full">
      <div className="relative h-[402px] w-full max-w-[602px] mx-auto">
        {/* Main Group Card */}
        <div className="absolute bg-gradient-to-b from-white/80 to-[#ccd0ff]/80 h-[407px] left-1/2 transform -translate-x-1/2 top-0 w-[276px] rounded-[30px] shadow-lg">
          {/* Group Content */}
          <div className="absolute h-[227px] left-0 top-[180px] w-[276px]">
            {/* Add Member Button */}
            <div className="absolute left-28 top-[182px] w-[45px] h-[45px]">
              <div className="absolute bottom-0 left-1/2 transform -translate-x-1/2 w-[45px] h-[45px]">
                <img alt="Add member" className="w-full h-full object-cover rounded-full" src={imgEllipse15} />
              </div>
              <div className="absolute w-7 h-7 transform -translate-x-1/2 -translate-y-1/2 top-1/2 left-1/2">
                <div className="absolute left-1/2 top-1/2 transform -translate-x-1/2 -translate-y-1/2 w-3.5 h-3.5">
                  <img alt="Plus icon" className="w-full h-full" src={imgPlus} />
                </div>
              </div>
            </div>
            
            {/* Group Info */}
            <div className="absolute h-[152px] left-0 top-0 w-[276px]">
              <div className="absolute font-semibold text-black text-[18px] text-left w-[141px] top-0 left-1/2 transform -translate-x-1/2">
                <p className="leading-[20px]">Beginner-Friendly</p>
              </div>
              <div className="absolute font-normal text-black text-[12px] text-center top-11 left-1/2 transform -translate-x-1/2 w-[181px]">
                <p className="leading-[12px] mb-0">
                  <span className="font-semibold">Stand-up Starter Hub</span>
                  <span>
                    <br /> For complete beginners—share basic tips, joke structure, common
                    pacing mistakes.
                  </span>
                </p>
                <p className="block leading-[12px] mb-0">&nbsp;</p>
                <p className="leading-[12px]">
                  <span className="font-semibold">5-Minute Bit Workshop</span>
                  <span>
                    <br /> Weekly timed writing challenge where everyone submits a 5-minute
                    set on a given topic for peer review.
                  </span>
                </p>
              </div>
              
              {/* Navigation Buttons */}
              <button className="absolute block cursor-pointer left-[245px] w-[31px] h-[31px] top-[94px]">
                <img alt="Next" className="w-full h-full" src={imgFrame2609129} />
              </button>
              <div className="absolute flex items-center justify-center left-0 w-[31px] h-[31px] top-[94px]">
                <div className="flex-none rotate-[180deg] scale-y-[-100%]">
                  <button className="block cursor-pointer relative w-[31px] h-[31px]">
                    <img alt="Previous" className="w-full h-full" src={imgFrame2609130} />
                  </button>
                </div>
              </div>
            </div>
          </div>
          
          {/* Group Avatar */}
          <div className="absolute h-[130px] left-[69px] shadow-lg top-0 w-[131px]">
            <div className="absolute w-[130px] h-[130px] top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
              <img alt="Group avatar" className="w-full h-full object-cover rounded-full" src={imgEllipse18} />
            </div>
          </div>
        </div>
        
        {/* Member Avatars - Top Row */}
        <div className="absolute w-[100px] h-[100px] top-[calc(50%-93px)] left-[calc(50%+124px)] transform -translate-x-1/2 -translate-y-1/2">
          <img alt="Member" className="w-full h-full object-cover rounded-full" src={imgEllipse16} />
        </div>
        <div className="absolute w-[100px] h-[100px] top-[calc(50%-93px)] left-[calc(50%-137px)] transform -translate-x-1/2 -translate-y-1/2">
          <img alt="Member" className="w-full h-full object-cover rounded-full" src={imgEllipse17} />
        </div>
        
        {/* Member Avatars - Bottom Row */}
        <div className="absolute w-20 h-20 top-[calc(50%+13px)] left-[calc(50%+191px)] transform -translate-x-1/2 -translate-y-1/2">
          <img alt="Member" className="w-full h-full object-cover rounded-full" src={imgEllipse19} />
        </div>
        <div className="absolute w-[81px] h-20 top-[calc(50%+13px)] left-[calc(50%-205.5px)] transform -translate-x-1/2 -translate-y-1/2">
          <img alt="Member" className="w-full h-full object-cover rounded-full" src={imgEllipse14} />
        </div>
      </div>
      
      {/* Additional Member Avatars */}
      <div className="absolute w-[81px] h-20 top-[calc(50%+90.5px)] left-[calc(50%-256.5px)] transform -translate-x-1/2 -translate-y-1/2">
        <img alt="Member" className="w-full h-full object-cover rounded-full" src={imgEllipse20} />
      </div>
      <div className="absolute w-[81px] h-20 top-[calc(50%+90.5px)] left-[calc(50%+257.5px)] transform -translate-x-1/2 -translate-y-1/2">
        <img alt="Member" className="w-full h-full object-cover rounded-full" src={imgEllipse21} />
      </div>
    </div>
  );
}

const Groups: React.FC<GroupsProps> = ({ onNavigate }) => {
  return (
    <div className="bg-white min-h-screen flex flex-col">
      <Header title="Groups" onNavigate={onNavigate} />

      {/* Main Content */}
      <main className="flex-grow overflow-y-auto p-4 space-y-6 pb-24">
        {/* Background Pattern */}
        <div className="absolute top-0 left-1/2 transform -translate-x-1/2 w-[560px] h-[608px] opacity-10 pointer-events-none">
          <img alt="Background pattern" className="w-full h-full object-cover" src={imgVector5} />
        </div>

        {/* My Group Section */}
        <div className="relative bg-white rounded-xl p-6 border border-gray-200 shadow-sm">
          <h2 className="font-display text-xl font-semibold text-gray-900 mb-4 text-center">My Group</h2>
          
          {/* My Group Members */}
          <div className="flex justify-center items-center space-x-4 mb-6">
            <div className="w-[50px] h-[50px]">
              <img alt="Member" className="w-full h-full object-cover rounded-full" src={imgEllipse22} />
            </div>
            <div className="w-[50px] h-[50px]">
              <img alt="Member" className="w-full h-full object-cover rounded-full" src={imgEllipse23} />
            </div>
            <div className="w-[51px] h-[50px]">
              <img alt="Member" className="w-full h-full object-cover rounded-full" src={imgEllipse24} />
            </div>
          </div>
        </div>

        {/* Discover Groups Section */}
        <div className="relative bg-white rounded-xl p-6 border border-gray-200 shadow-sm">
          <h2 className="font-display text-xl font-semibold text-gray-900 mb-4 text-center">Discover Groups</h2>
          
          {/* Groups Scroll Area */}
          <div className="h-[429px] overflow-y-auto">
            <ScrollPage />
          </div>
        </div>

        {/* Join Groups CTA */}
        <div className="bg-white rounded-xl p-6 border border-gray-200 shadow-sm">
          <h3 className="font-display text-lg font-semibold text-gray-900 mb-4">Join More Groups</h3>
          <p className="text-[14px] mb-6 text-gray-700">Connect with fellow comedy enthusiasts and performers. Share jokes, plan meetups, and find your next open mic.</p>
          <button className="bg-[#636ae8] text-white text-[14px] px-6 py-2 rounded-md hover:bg-[#5a61d9] transition-colors">
            Browse All Groups
          </button>
        </div>
      </main>

      {/* Bottom Navigation */}
      <BottomNav onNavigate={onNavigate} currentView="groups" />
    </div>
  );
};

export default Groups;
