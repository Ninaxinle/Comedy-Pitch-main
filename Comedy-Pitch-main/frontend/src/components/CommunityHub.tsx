import React from "react";
import { BottomNav } from "./upload/BottomNav";
import Header from "./Header";

interface CommunityHubProps {
  onNavigate: (destination: string, params?: { [key: string]: any }) => void;
}

// Asset constants from Figma
const imgImage2 = "http://localhost:3845/assets/eed705f83aa8cdab3f67c77782476009f78f6c4b.png";
const imgImage3 = "http://localhost:3845/assets/47ef79407bcdb616109dc766018964de8dc5ec9c.png";
const imgImage4 = "http://localhost:3845/assets/c909dffb438fae3efee09aaf9d0eccaba9996ac2.png";
const imgImage1 = "http://localhost:3845/assets/382bb03bdd3527bbc9b7800a7c4465830a40afb5.png";
const imgEllipse10 = "http://localhost:3845/assets/cdd6cdf24b18ba8624e666a691044ddeccde9739.png";
const imgImage5 = "http://localhost:3845/assets/1ef1494000efe6a2765ce8775b5180c818d5d9ff.png";
const imgEllipse12 = "http://localhost:3845/assets/f0d3584865662d84e0f9e053c2e3320ca498a069.png";
const imgImage6 = "http://localhost:3845/assets/2d42cd02beeaa3c7652b5d96fae1522147f58fd5.png";
const imgEllipse17 = "http://localhost:3845/assets/22b5955c1820889847577d39560070f054de6ae9.png";
const imgVector = "http://localhost:3845/assets/1c7ed08e5108ca219584918d9d2017a47e7901c6.svg";
const imgVector1 = "http://localhost:3845/assets/87bd8c8c474ac117e28005987c69b5f9e6b71eee.svg";
const imgGroup = "http://localhost:3845/assets/afa5d24371909d27c28c8469fc8a03681c1dec56.svg";
const imgGroup1 = "http://localhost:3845/assets/1014bac52cc589a40c066a5504f5a1b9982b5ef1.svg";
const imgVector2 = "http://localhost:3845/assets/7feeb923fa949aebe447f3addcf25666c7cc1dd3.svg";
const imgVector3 = "http://localhost:3845/assets/b0e01994db71721e33912cfb9b3298ad3e698d0c.svg";
const imgVector4 = "http://localhost:3845/assets/1745c2d7e0cc18aedbb78dd65785c1978ea29442.svg";
const imgVector5 = "http://localhost:3845/assets/b8c8047b8cad0b721327e0d67b911aee88859c01.svg";
const imgVector6 = "http://localhost:3845/assets/64fe19985a26825a6496d4dc3c83bef8e3933f1c.svg";
const imgGroup2 = "http://localhost:3845/assets/0e79831c5b79cd061c363bbd89b9f24ebdd6f061.svg";
const imgVector7 = "http://localhost:3845/assets/17168a421b6cf74835a35a51c227da7f5e03beb0.svg";
const imgGardenUserFollowStroke12 = "http://localhost:3845/assets/c360d9c7046fda95a7903d033fc80fa1765b00c5.svg";
const imgEllipse11 = "http://localhost:3845/assets/e59a7b86c55f10016b1a3ca21aade4508cc59476.svg";
const imgLine4 = "http://localhost:3845/assets/c9e13f7b17ba5611d5614657836091c816d92b07.svg";
const imgLine7 = "http://localhost:3845/assets/aec21859b288deeddb32e7329119e566c8d69da5.svg";
const imgLine8 = "http://localhost:3845/assets/fa0d64fe5982f047e3d239f647d8263ef400fb34.svg";
const imgEllipse13 = "http://localhost:3845/assets/0cca30d7b0a07f78fc0834798e45c323edcecdca.svg";
const imgEllipse14 = "http://localhost:3845/assets/7b95b39d0e634c6d92d479084440574c1a6aebca.svg";
const imgStreamlineKameleonColorLoveSmiley = "http://localhost:5173/assets/streamline-kameleon-color_love-smiley.svg";
const fluentEmojiHotFace = "http://localhost:5173/assets/fluent-emoji_hot-face.svg";
const devIconLove2D = "http://localhost:5173/assets/devicon_love2d.svg";
const imgLine3 = "http://localhost:3845/assets/0e793cb3a45fa96975e9d26bb1f4540e58cb4b6e.svg";
const imgVector13 = "http://localhost:3845/assets/5d416c30fee12a3cb245d00102c5b456df5f515f.svg";
const imgEllipse15 = "http://localhost:3845/assets/de6bf15d30b8c69444534868d1830cc38a723a3a.svg";
const imgEllipse16 = "http://localhost:3845/assets/0f9f7d4ef177d606412da6b3fb8ff4c07417a14c.svg";
const imgLine6 = "http://localhost:3845/assets/d65f46f8479016995afb9ce86bd5343e7cb18b68.svg";
const img35 = "http://localhost:3845/assets/1c12c0ed68d44667ae760f96161652cb71342059.svg";
const img = "http://localhost:3845/assets/9c7bbde64348ea1e54774f2f74b7547f1331af4c.svg";
const imgVector11 = "http://localhost:3845/assets/5b5ccdb524c1a20395396c96d6a461b6a3487d16.svg";
const imgVector12 = "http://localhost:3845/assets/9930ac12a3c5a10c4ee998ce73a9fbf997426315.svg";
const imgFrame = "http://localhost:3845/assets/8c44af008dab2ac0792926717eb708b62eb36c4c.svg";
const imgGroup4 = "http://localhost:3845/assets/075ecd48288bfedcbb3128f68da200ed882004ee.svg";

// Component interfaces
interface AllProps {
  property1?: "Default" | "Variant2";
}

function All({ property1: _property1 = "Default" }: AllProps) {
  return (
    <button className="cursor-pointer relative rounded-[20px] size-full">
      <div className="overflow-clip relative size-full">
        <div
          className="absolute font-['Myriad_Pro:Regular',_sans-serif] leading-[0] left-1/2 not-italic text-[#000000] text-[18px] text-center text-nowrap translate-x-[-50%]"
          style={{ top: "calc(50% - 8px)" }}
        >
          <p className="block leading-[16px] whitespace-pre">All</p>
        </div>
      </div>
      <div
        className="absolute border border-[#979797] border-solid inset-0 pointer-events-none rounded-[20px]"
      />
    </button>
  );
}

interface ComedyClubsProps {
  property1?: "Default" | "Variant2";
}

function ComedyClubs({ property1: _property1 = "Default" }: ComedyClubsProps) {
  return (
    <button className="cursor-pointer relative rounded-[20px] size-full">
      <div className="overflow-clip relative size-full">
        <div
          className="absolute font-['Myriad_Pro:Regular',_sans-serif] leading-[0] not-italic text-[#000000] text-[18px] text-center text-nowrap translate-x-[-50%]"
          style={{ top: "calc(50% - 8px)", left: "calc(50% + 0.5px)" }}
        >
          <p className="block leading-[16px] whitespace-pre">Comedy Clubs</p>
        </div>
      </div>
      <div
        className="absolute border border-[#979797] border-solid inset-0 pointer-events-none rounded-[20px]"
      />
    </button>
  );
}

function MaterialSymbolsSearch() {
  return (
    <div className="relative size-full">
      <div className="absolute left-1/2 size-6 top-1/2 translate-x-[-50%] translate-y-[-50%]">
        <img alt className="block max-w-none size-full" src={imgVector} />
      </div>
    </div>
  );
}

function LsiconDownOutline() {
  return (
    <div className="relative size-full">
      <div className="absolute inset-[37.5%_28.13%_40.63%_28.13%]">
        <div className="absolute inset-[-12.93%_-6.46%_-25.86%_-6.46%]">
          <img alt className="block max-w-none size-full" src={imgVector1} />
        </div>
      </div>
    </div>
  );
}

function SolarCalendarLinear() {
  return (
    <div className="relative size-full">
      <div className="absolute inset-[10.42%_8.33%_8.33%_8.33%]">
        <div className="absolute inset-[-5.77%_-5.63%]">
          <img alt className="block max-w-none size-full" src={imgGroup} />
        </div>
      </div>
    </div>
  );
}

function MingcuteLocationFill() {
  return (
    <div className="relative size-full">
      <div className="absolute h-4 left-px top-4 w-[190px]">
        <div
          className="absolute font-['Myriad_Pro:Regular',_sans-serif] leading-[0] not-italic text-[#000000] text-[14px] text-left top-0 w-[167px]"
          style={{ left: "calc(50% - 72px)" }}
        >
          
        </div>
        <div className="absolute bottom-[0.78%] left-0 right-[93.72%] top-[8.33%]">
          <img alt className="block max-w-none size-full" src={imgGroup1} />
        </div>
      </div>
    </div>
  );
}

function MaterialSymbolsAttachMoneyRounded() {
  return (
    <div className="relative size-full">
      <div className="absolute inset-[12.5%_30.52%_12.5%_31.6%]">
        <img alt className="block max-w-none size-full" src={imgVector2} />
      </div>
    </div>
  );
}

function UilMessage() {
  return (
    <div className="relative size-full">
      <div className="absolute inset-[8.36%_8.33%_8.33%_8.34%]">
        <img alt className="block max-w-none size-full" src={imgVector3} />
      </div>
    </div>
  );
}

function DeviconLove2D() {
  return (
    <div className="relative size-full">
      <div className="absolute bottom-[9.24%] left-0 right-[14.7%] top-0">
        <img alt className="block max-w-none size-full" src={imgVector4} />
      </div>
      <div className="absolute bottom-0 left-[21.31%] right-0 top-[14.37%]">
        <img alt className="block max-w-none size-full" src={imgVector5} />
      </div>
      <div className="absolute inset-[29.05%_23.2%_22.76%_23.25%]">
        <img alt className="block max-w-none size-full" src={imgVector6} />
      </div>
    </div>
  );
}

function FluentEmojiHotFace() {
  return (
    <div className="relative size-full">
      <div className="absolute inset-[6.25%_6.25%_6.26%_6.25%]">
        <img alt className="block max-w-none size-full" src={imgGroup2} />
      </div>
    </div>
  );
}

function IconamoonComment() {
  return (
    <div className="relative size-full">
      <div className="absolute inset-[12.5%]">
        <div className="absolute inset-[-5.56%]">
          <img alt className="block max-w-none size-full" src={imgVector7} />
        </div>
      </div>
    </div>
  );
}

const CommunityHub: React.FC<CommunityHubProps> = ({ onNavigate }) => {
  return (
    <div className="bg-white min-h-screen flex flex-col">
      <Header title="Community Hub" onNavigate={onNavigate} customIcon={null} />

      {/* Main Content */}
      <main className="flex-grow overflow-y-auto p-4 space-y-6 pb-24">
        {/* Search and Filters Section */}
        <div className="bg-white rounded-xl p-6 border border-gray-200 shadow-sm">
          <h3 className="font-display text-lg font-semibold text-gray-900 mb-4">Search & Filters</h3>
          
          {/* Search Bar */}
          <div className="relative mb-4">
            <div className="bg-gray-50 h-[45px] rounded-[10px] flex items-center px-4">
              <div className="mr-3">
                <MaterialSymbolsSearch />
              </div>
              <input
                type="text"
                placeholder="Search Comedy Bits"
                className="flex-1 bg-transparent text-gray-700 placeholder-gray-500 focus:outline-none"
              />
              <div className="ml-3">
                <LsiconDownOutline />
              </div>
            </div>
          </div>

          {/* Category Tags */}
          <div className="flex gap-3 mb-4 overflow-x-auto">
            <div className="h-[30px] rounded-[20px] min-w-[50px]">
              <All />
            </div>
            <div className="h-[30px] rounded-[20px] min-w-[136px]">
              <ComedyClubs />
            </div>
            <div className="h-[30px] rounded-[20px] min-w-[102px]">
              <div className="h-[30px] overflow-clip relative w-[102px]">
                <div className="absolute font-['Myriad_Pro:Regular',_sans-serif] leading-[0] not-italic text-[#000000] text-[18px] text-center text-nowrap translate-x-[-50%]" style={{ top: "calc(50% - 8px)", left: "calc(50% + 0.5px)" }}>
                  <p className="block leading-[16px] whitespace-pre">Open Mic</p>
                </div>
              </div>
            </div>
            <div className="h-[30px] rounded-[20px] min-w-[102px]">
              <div className="h-[30px] overflow-clip relative w-[102px]">
                <div className="absolute font-['Myriad_Pro:Regular',_sans-serif] leading-[0] not-italic text-[#000000] text-[18px] text-center text-nowrap translate-x-[-50%]" style={{ top: "calc(50% - 8px)", left: "calc(50% + 0.5px)" }}>
                  <p className="block leading-[16px] whitespace-pre">Character</p>
                </div>
              </div>
            </div>
            <div className="h-[30px] rounded-[20px] min-w-[74px]">
              <div className="h-[30px] overflow-clip relative w-[74px]">
                <div className="absolute font-['Myriad_Pro:Regular',_sans-serif] leading-[0] left-1/2 not-italic text-[#000000] text-[18px] text-center text-nowrap translate-x-[-50%]" style={{ top: "calc(50% - 8px)" }}>
                  <p className="block leading-[16px] whitespace-pre">Show</p>
                </div>
              </div>
            </div>
            <div className="h-[30px] rounded-[20px] min-w-[122px]">
              <div className="h-[30px] overflow-clip relative w-[122px]">
                <div className="absolute font-['Myriad_Pro:Regular',_sans-serif] leading-[0] left-1/2 not-italic text-[#000000] text-[18px] text-center text-nowrap translate-x-[-50%]" style={{ top: "calc(50% - 8px)" }}>
                  <p className="block leading-[16px] whitespace-pre">Dark Comedy</p>
                </div>
              </div>
            </div>
            <div className="h-[30px] rounded-[20px] min-w-[147px]">
              <div className="h-[30px] overflow-clip relative w-[147px]">
                <div className="absolute font-['Myriad_Pro:Regular',_sans-serif] leading-[0] not-italic text-[#000000] text-[18px] text-center text-nowrap translate-x-[-50%]" style={{ top: "calc(50% - 8px)", left: "calc(50% + 0.5px)" }}>
                  <p className="block leading-[16px] whitespace-pre">Satirical Comedy</p>
                </div>
              </div>
            </div>
            <div className="h-[30px] rounded-[20px] min-w-[181px]">
              <div className="h-[30px] overflow-clip relative w-[181px]">
                <div className="absolute font-['Myriad_Pro:Regular',_sans-serif] leading-[0] not-italic text-[#000000] text-[18px] text-center text-nowrap translate-x-[-50%]" style={{ top: "calc(50% - 8px)", left: "calc(50% - 0.5px)" }}>
                  <p className="block leading-[16px] whitespace-pre">Storytelling Comedy</p>
                </div>
              </div>
            </div>
            <div className="h-[30px] rounded-[20px] min-w-[204px]">
              <div className="h-[30px] overflow-clip relative w-[204px]">
                <div className="absolute font-['Myriad_Pro:Regular',_sans-serif] leading-[0] left-1/2 not-italic text-[#000000] text-[18px] text-center text-nowrap translate-x-[-50%]" style={{ top: "calc(50% - 8px)" }}>
                  <p className="block leading-[16px] whitespace-pre">Observational Comedy</p>
                </div>
              </div>
            </div>
          </div>

          {/* Filter Buttons */}
          <div className="flex gap-3">
            <button className="bg-gray-50 h-10 px-4 rounded-md flex items-center gap-2 border border-gray-200">
              <div className="size-4">
                <img alt className="block max-w-none size-full" src={imgFrame} />
              </div>
              <span className="text-[14px] text-gray-700">Category</span>
            </button>
            
            <button className="bg-gray-50 h-10 px-4 rounded-md flex items-center gap-2 border border-gray-200">

              <span className="text-[14px] text-gray-700">Duration</span>
            </button>
          </div>
        </div>

        {/* Community Spotlight Section */}
        <div className="bg-white rounded-xl p-6 border border-gray-200 shadow-sm">
          <h3 className="font-display text-lg font-semibold text-gray-900 mb-4">Community Spotlight</h3>
          
          {/* Comedy Posts Feed - Horizontal Scroll */}
          <div className="overflow-x-auto">
            <div className="flex gap-4 min-w-max">
              {/* Post 1 - Mya Rodriguez */}
              <div className="bg-gray-50 rounded-[10px] p-4 border border-gray-200 w-[300px] flex-shrink-0">
                {/* User Header */}
                <div className="flex items-center mb-4">
                  <img alt="User avatar" className="w-[45px] h-[45px] rounded-full" src={imgEllipse10} />
                  <div className="ml-4">
                    <h3 className="font-semibold text-[16px]">Mya Rodriguez</h3>
                    <div className="flex gap-2 mt-2">
                      <button className="px-3 py-1 text-xs rounded-[5px] border border-gray-300 flex items-center bg-white">
                        <img alt className="w-3 h-3 mr-1" src={imgGardenUserFollowStroke12} />
                        Follow
                      </button>
                      <button className="px-3 py-1 text-xs rounded-[5px] border border-gray-300 flex items-center bg-white">
                        <UilMessage />
                        Message
                      </button>
                    </div>
                  </div>
                </div>

                {/* Post Image */}
                <div className="w-full h-[197px] bg-cover bg-center rounded-[10px] mb-4" style={{ backgroundImage: `url('${imgImage1}')` }} />

                {/* Post Content */}
                <h3 className="font-semibold text-[20px] mb-2">Laugh Riot: The Daily Grind</h3>
                <p className="text-[14px] mb-4 text-gray-700">A hilarious take on everyday absurdities, from commuting woes to digital detox attempts.</p>

                {/* Tags */}
                <div className="flex gap-2 mb-4">
                  <span className="text-[14px] text-gray-600">60 mins</span>
                  <span className="w-1.5 h-1.5 rounded-full bg-gray-400 self-center" />
                  <span className="text-[14px] text-gray-600">Observational</span>
                  <span className="w-1.5 h-1.5 rounded-full bg-gray-400 self-center" />
                  <span className="text-[14px] text-gray-600">Daily Life</span>
                </div>

                {/* Engagement Stats */}
                <div className="flex items-center gap-6 text-[#979797]">
                  <div className="flex items-center gap-2">
                    <img alt className="w-4 h-4" src={imgVector11} />
                    <span>253</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <IconamoonComment />
                    <span>631</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <img alt className="w-3 h-4" src={imgVector12} />
                    <span>15</span>
                  </div>
                </div>

                {/* Horizontal Line */}
                <div className="border-t border-gray-200 my-4 w-full"></div>

                {/* Comment Section */}
                <div className="mt-4 pt-4 border-t border-gray-200">
                  <h4 className="text-[12px] font-medium mb-2 whitespace-nowrap">Comment Highlights:</h4>
                  <div className="flex gap-2 mb-3">
                    <span className="bg-[#ccd0ff] text-[14px] px-3 py-1 rounded-[5px]">60 mins</span>
                    <span className="bg-[#ccd0ff] text-[14px] px-3 py-1 rounded-[5px]">Observational</span>
                    <span className="bg-[#ccd0ff] text-[14px] px-3 py-1 rounded-[5px]">Daily Life</span>
                  </div>
                  
                  {/* Comments */}
                  <div className="space-y-3">
                    <div className="flex gap-3">
                      <img alt="User" className="w-7 h-7 rounded-full" src={imgEllipse13} />
                      <div className="flex-1">
                        <div className="font-medium text-[20px]">New Comic Hopeful</div>
                                                                                    <div className="text-[14px] text-gray-700">I'll be there ! First time performing wish me luck !</div>
                        
                        {/* Horizontal Line */}
                        <div className="border-t border-gray-200 my-2 w-full"></div>
                        
                        <div className="flex gap-2 mt-2">
                                      <div className="bg-[#ebebea] h-[30px] w-[142px] rounded-[20px]"></div>
                                      {/* <DeviconLove2D /> */}
                                      {/* <FluentEmojiHotFace /> */}
                                      <img alt="Love" className="w-4 h-4" src={devIconLove2D} />
                                      <img alt="Hot" className="w-4 h-4" src={fluentEmojiHotFace} />
                                      <img alt="Smiley" className="w-4 h-4" src={imgStreamlineKameleonColorLoveSmiley} />
                                    </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Post 2 - Ben Carter */}
              <div className="bg-gray-50 rounded-[10px] p-4 border border-gray-200 w-[300px] flex-shrink-0">
                {/* User Header */}
                <div className="flex items-center mb-4">
                  <img alt="User avatar" className="w-[45px] h-[45px] rounded-full" src={imgEllipse12} />
                  <div className="ml-4">
                    <h3 className="font-semibold text-[16px]">Ben Carter</h3>
                    <div className="flex gap-2 mt-2">
                      <button className="px-3 py-1 text-xs rounded-[5px] border border-gray-300 flex items-center bg-white">
                        <img alt className="w-3 h-3 mr-1" src={imgGardenUserFollowStroke12} />
                        Follow
                      </button>
                      <button className="px-3 py-1 text-xs rounded-[5px] border border-gray-300 flex items-center bg-white">
                        <UilMessage />
                        Message
                      </button>
                    </div>
                  </div>
                </div>

                {/* Post Image */}
                <div className="w-full h-[197px] bg-cover bg-center rounded-[10px] mb-4" style={{ backgroundImage: `url('${imgImage5}')` }} />

                {/* Post Content */}
                <h3 className="font-semibold text-[20px] mb-2">The Existential Heckle</h3>
                <p className="text-[14px] mb-4 text-gray-700">Ben delves deep into the absurdities of existence with a dry wit and philosophical flair.</p>

                {/* Tags */}
                <div className="flex gap-2 mb-4">
                  <span className="text-[14px] text-gray-600">75 mins</span>
                  <span className="w-1.5 h-1.5 rounded-full bg-gray-400 self-center" />
                  <span className="text-[14px] text-gray-600">Philosophical</span>
                  <span className="w-1.5 h-1.5 rounded-full bg-gray-400 self-center" />
                  <span className="text-[14px] text-gray-600">Existential</span>
                </div>

                {/* Engagement Stats */}
                <div className="flex items-center gap-6 text-[#979797]">
                  <div className="flex items-center gap-2">
                    <img alt className="w-4 h-4" src={imgVector13} />
                    <span>98</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <IconamoonComment />
                    <span>200</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <img alt className="w-3 h-4" src={imgVector12} />
                    <span>90</span>
                  </div>
                </div>

                {/* Horizontal Line */}
                <div className="border-t border-gray-200 my-4 w-full"></div>

                {/* Comment Section */}
                <div className="mt-4 pt-4 border-t border-gray-200">
                  <h4 className="text-[12px] font-medium mb-2 whitespace-nowrap">Comment Highlights:</h4>
                  <div className="flex gap-2 mb-3">
                    <span className="bg-[#ccd0ff] text-[14px] px-3 py-1 rounded-[5px]">Deep</span>
                    <span className="bg-[#ccd0ff] text-[14px] px-3 py-1 rounded-[5px]">clever</span>
                    <span className="bg-[#ccd0ff] text-[14px] px-3 py-1 rounded-[5px]">thought-Provoking</span>
                  </div>
                  
                  {/* Comments */}
                  <div className="space-y-3">
                    <div className="flex gap-3">
                      <img alt="User" className="w-7 h-7 rounded-full" src={imgEllipse15} />
                      <div className="flex-1">
                        <div className="font-medium text-[20px]">Laugh Master</div>
                        <div className="text-[14px] text-gray-700">So true ! The accuracy of her set is incredible.</div>
                        
                        {/* Horizontal Line */}
                        <div className="border-t border-gray-200 my-2 w-full"></div>
                        
                        <div className="flex gap-2 mt-2">
                          <div className="bg-[#ebebea] h-[30px] w-[142px] rounded-[20px]"></div>
                          <img alt="Love" className="w-4 h-4" src={devIconLove2D} />
                          <img alt="Hot" className="w-4 h-4" src={fluentEmojiHotFace} />
                          <img alt="Smiley" className="w-4 h-4" src={imgStreamlineKameleonColorLoveSmiley} />
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Post 3 - Chloe Kim */}
              <div className="bg-gray-50 rounded-[10px] p-4 border border-gray-200 w-[300px] flex-shrink-0">
                {/* User Header */}
                <div className="flex items-center mb-4">
                  <img alt="User avatar" className="w-[45px] h-[45px] rounded-full" src={imgEllipse17} />
                  <div className="ml-4">
                    <h3 className="font-semibold text-[16px]">Chloe Kim</h3>
                    <div className="flex gap-2 mt-2">
                      <button className="px-3 py-1 text-xs rounded-[5px] border border-gray-300 flex items-center bg-white">
                        <img alt className="w-3 h-3 mr-1" src={imgGardenUserFollowStroke12} />
                        Follow
                      </button>
                      <button className="px-3 py-1 text-xs rounded-[5px] border border-gray-300 flex items-center bg-white">
                        <UilMessage />
                        Message
                      </button>
                    </div>
                  </div>
                </div>

                {/* Post Image */}
                <div className="w-full h-[197px] bg-cover bg-center rounded-[10px] mb-4" style={{ backgroundImage: `url('${imgImage6}')` }} />

                {/* Post Content */}
                <h3 className="font-semibold text-[20px] mb-2">Character Showcase: Unhinged Neighbors</h3>
                <p className="text-[14px] mb-4 text-gray-700">Chloe brings to life a cast of unforgettable characters inspired by her chaotic apartment building</p>

                {/* Tags */}
                <div className="flex gap-2 mb-4">
                  <span className="text-[14px] text-gray-600">30 mins</span>
                  <span className="w-1.5 h-1.5 rounded-full bg-gray-400 self-center" />
                  <span className="text-[14px] text-gray-600">Character</span>
                  <span className="w-1.5 h-1.5 rounded-full bg-gray-400 self-center" />
                  <span className="text-[14px] text-gray-600">Urban Living</span>
                </div>

                {/* Engagement Stats */}
                <div className="flex items-center gap-6 text-[#979797]">
                  <div className="flex items-center gap-2">
                    <img alt className="w-4 h-4" src={imgVector13} />
                    <span>30</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <IconamoonComment />
                    <span>150</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <img alt className="w-3 h-4" src={imgVector12} />
                    <span>30</span>
                  </div>
                </div>

                {/* Horizontal Line */}
                <div className="border-t border-gray-200 my-4 w-full"></div>

                {/* Comment Section */}
                <div className="mt-4 pt-4 border-t border-gray-200">
                  <h4 className="text-[12px] font-medium mb-2 whitespace-nowrap">Comment Highlights:</h4>
                  <div className="flex gap-2 mb-3">
                    <span className="bg-[#ccd0ff] text-[14px] px-3 py-1 rounded-[5px]">Spot On</span>
                    <span className="bg-[#ccd0ff] text-[14px] px-3 py-1 rounded-[5px]">Unique</span>
                    <span className="bg-[#ccd0ff] text-[14px] px-3 py-1 rounded-[5px]">Funny Voices</span>
                  </div>
                  
                  {/* Comments */}
                  <div className="space-y-3">
                    <div className="flex gap-3">
                      <img alt="User" className="w-7 h-7 rounded-full" src={imgEllipse13} />
                      <div className="flex-1">
                        <div className="font-medium text-[20px]">Comedy Critique</div>
                        <div className="text-[14px] text-gray-700">She never misses ! Need to see her live.</div>
                        
                        {/* Horizontal Line */}
                        <div className="border-t border-gray-200 my-2 w-full"></div>
                        
                        <div className="flex gap-2 mt-2">
                          <div className="bg-[#ebebea] h-[30px] w-[142px] rounded-[20px]"></div>
                          <img alt="Love" className="w-4 h-4" src={devIconLove2D} />
                          <img alt="Hot" className="w-4 h-4" src={fluentEmojiHotFace} />
                          <img alt="Smiley" className="w-4 h-4" src={imgStreamlineKameleonColorLoveSmiley} />
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                                        </div>

                          {/* Post 4 - Alex Thompson */}
                          <div className="bg-gray-50 rounded-[10px] p-4 border border-gray-200 w-[300px] flex-shrink-0">
                            {/* User Header */}
                            <div className="flex items-center mb-4">
                              <img alt="User avatar" className="w-[45px] h-[45px] rounded-full" src={imgEllipse10} />
                              <div className="ml-4">
                                <h3 className="font-semibold text-[16px]">Alex Thompson</h3>
                                <div className="flex gap-2 mt-2">
                                  <button className="px-3 py-1 text-xs rounded-[5px] border border-gray-300 flex items-center bg-white">
                                    <svg className="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                                      <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                                    </svg>
                                    Follow
                                  </button>
                                  <button className="px-3 py-1 text-xs rounded-[5px] border border-gray-300 flex items-center bg-white">
                                    <svg className="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                                      <path d="M2.003 5.884L10 9.882l7.997-3.998A2 2 0 0016 4H4a2 2 0 00-1.997 1.884z" />
                                      <path d="M18 8.118l-8 4-8-4V14a2 2 0 002 2h12a2 2 0 002-2V8.118z" />
                                    </svg>
                                    Message
                                  </button>
                                </div>
                              </div>
                            </div>

                            {/* Post Image */}
                            <div className="w-full h-[197px] bg-cover bg-center rounded-[10px] mb-4" style={{ backgroundImage: `url('${imgImage1}')` }} />

                            {/* Post Content */}
                            <h3 className="font-semibold text-[20px] mb-2">Tech Comedy: Digital Life</h3>
                            <p className="text-[14px] mb-4 text-gray-700">Hilarious observations about our relationship with technology, from social media addiction to smart home fails.</p>

                            {/* Tags */}
                            <div className="flex gap-2 mb-4">
                              <span className="text-[14px] text-gray-600">45 mins</span>
                              <span className="w-1.5 h-1.5 rounded-full bg-gray-400 self-center" />
                              <span className="text-[14px] text-gray-600">Tech</span>
                              <span className="w-1.5 h-1.5 rounded-full bg-gray-400 self-center" />
                              <span className="text-[14px] text-gray-600">Modern Life</span>
                            </div>

                                            {/* Engagement Stats */}
                <div className="flex items-center gap-6 text-[#979797]">
                  <div className="flex items-center gap-2">
                    <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M2 10.5a1.5 1.5 0 113 0v6a1.5 1.5 0 01-3 0v-6zM6 10.333v5.43a2 2 0 001.106 1.79l.05.025A4 4 0 008.943 18h5.416a2 2 0 001.962-1.608l1.2-6A2 2 0 0015.56 8H12V4a2 2 0 00-2-2 1 1 0 00-1 1v.667a4 4 0 01-.8 2.4L6.8 7.933a4 4 0 00-.8 2.4z" />
                    </svg>
                    <span>187</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M18 10c0 3.866-3.582 7-8 7a8.841 8.841 0 01-4.083-.98L2 17l1.338-3.123C2.493 12.767 2 11.434 2 10c0-3.866 3.582-7 8-7s8 3.134 8 7zM7 9H5v2h2V9zm8 0h-2v2h2V9zM9 9h2v2H9V9z" clipRule="evenodd" />
                    </svg>
                    <span>342</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M15 8a3 3 0 10-2.977-2.63l-4.94 2.47a3 3 0 100 4.319l4.94 2.47a3 3 0 10.895-1.789l-4.94-2.47a3.027 3.027 0 000-.74l4.94-2.47C13.456 7.68 14.19 8 15 8z" />
                    </svg>
                    <span>28</span>
                  </div>
                </div>

                {/* Horizontal Line */}
                <div className="border-t border-gray-200 my-4 w-full"></div>

                {/* Comment Section */}
                <div className="mt-4 pt-4 border-t border-gray-200">
                              <h4 className="text-[12px] font-medium mb-2 whitespace-nowrap">Comment Highlights:</h4>
                              <div className="flex gap-2 mb-3">
                                <span className="bg-[#ccd0ff] text-[14px] px-3 py-1 rounded-[5px]">Relatable</span>
                                <span className="bg-[#ccd0ff] text-[14px] px-3 py-1 rounded-[5px]">Smart</span>
                                <span className="bg-[#ccd0ff] text-[14px] px-3 py-1 rounded-[5px]">Tech Humor</span>
                              </div>
                              
                              {/* Comments */}
                              <div className="space-y-3">
                                <div className="flex gap-3">
                                  <img alt="User" className="w-7 h-7 rounded-full" src={imgEllipse13} />
                                  <div className="flex-1">
                                                            <div className="font-medium text-[20px]">Digital Nomad</div>
                        <div className="text-[14px] text-gray-700">This hits way too close to home! My Alexa is judging me.</div>
                        
                        {/* Horizontal Line */}
                        <div className="border-t border-gray-200 my-2 w-full"></div>
                        
                        <div className="flex gap-2 mt-2">
                          <div className="bg-[#ebebea] h-[30px] w-[142px] rounded-[20px]"></div>
                          <img alt="Love" className="w-4 h-4" src={devIconLove2D} />
                          <img alt="Hot" className="w-4 h-4" src={fluentEmojiHotFace} />
                          <img alt="Smiley" className="w-4 h-4" src={imgStreamlineKameleonColorLoveSmiley} />
                        </div>
                                  </div>
                                </div>
                              </div>
                            </div>
                          </div>

                          {/* Post 5 - Sarah Chen */}
                          <div className="bg-gray-50 rounded-[10px] p-4 border border-gray-200 w-[300px] flex-shrink-0">
                            {/* User Header */}
                            <div className="flex items-center mb-4">
                              <img alt="User avatar" className="w-[45px] h-[45px] rounded-full" src={imgEllipse12} />
                              <div className="ml-4">
                                <h3 className="font-semibold text-[16px]">Sarah Chen</h3>
                                <div className="flex gap-2 mt-2">
                                  <button className="px-3 py-1 text-xs rounded-[5px] border border-gray-300 flex items-center bg-white">
                                    <svg className="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                                      <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                                    </svg>
                                    Follow
                                  </button>
                                  <button className="px-3 py-1 text-xs rounded-[5px] border border-gray-300 flex items-center bg-white">
                                    <svg className="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                                      <path d="M2.003 5.884L10 9.882l7.997-3.998A2 2 0 0016 4H4a2 2 0 00-1.997 1.884z" />
                                      <path d="M18 8.118l-8 4-8-4V14a2 2 0 002 2h12a2 2 0 002-2V8.118z" />
                                    </svg>
                                    Message
                                  </button>
                                </div>
                              </div>
                            </div>

                            {/* Post Image */}
                            <div className="w-full h-[197px] bg-cover bg-center rounded-[10px] mb-4" style={{ backgroundImage: `url('${imgImage5}')` }} />

                            {/* Post Content */}
                            <h3 className="font-semibold text-[20px] mb-2">Cultural Comedy Fusion</h3>
                            <p className="text-[14px] mb-4 text-gray-700">Sarah blends cultural observations with universal humor, creating comedy that bridges different worlds.</p>

                            {/* Tags */}
                            <div className="flex gap-2 mb-4">
                              <span className="text-[14px] text-gray-600">50 mins</span>
                              <span className="w-1.5 h-1.5 rounded-full bg-gray-400 self-center" />
                              <span className="text-[14px] text-gray-600">Cultural</span>
                              <span className="w-1.5 h-1.5 rounded-full bg-gray-400 self-center" />
                              <span className="text-[14px] text-gray-600">Family</span>
                            </div>

                                            {/* Engagement Stats */}
                <div className="flex items-center gap-6 text-[#979797]">
                  <div className="flex items-center gap-2">
                    <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M2 10.5a1.5 1.5 0 113 0v6a1.5 1.5 0 01-3 0v-6zM6 10.333v5.43a2 2 0 001.106 1.79l.05.025A4 4 0 008.943 18h5.416a2 2 0 001.962-1.608l1.2-6A2 2 0 0015.56 8H12V4a2 2 0 00-2-2 1 1 0 00-1 1v.667a4 4 0 01-.8 2.4L6.8 7.933a4 4 0 00-.8 2.4z" />
                    </svg>
                    <span>156</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M18 10c0 3.866-3.582 7-8 7a8.841 8.841 0 01-4.083-.98L2 17l1.338-3.123C2.493 12.767 2 11.434 2 10c0-3.866 3.582-7 8-7s8 3.134 8 7zM7 9H5v2h2V9zm8 0h-2v2h2V9zM9 9h2v2H9V9z" clipRule="evenodd" />
                    </svg>
                    <span>289</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M15 8a3 3 0 10-2.977-2.63l-4.94 2.47a3 3 0 100 4.319l4.94 2.47a3 3 0 10.895-1.789l-4.94-2.47a3.027 3.027 0 000-.74l4.94-2.47C13.456 7.68 14.19 8 15 8z" />
                    </svg>
                    <span>42</span>
                  </div>
                </div>

                {/* Horizontal Line */}
                <div className="border-t border-gray-200 my-4 w-full"></div>

                {/* Comment Section */}
                <div className="mt-4 pt-4 border-t border-gray-200">
                              <h4 className="text-[12px] font-medium mb-2 whitespace-nowrap">Comment Highlights:</h4>
                              <div className="flex gap-2 mb-3">
                                <span className="bg-[#ccd0ff] text-[14px] px-3 py-1 rounded-[5px]">Authentic</span>
                                <span className="bg-[#ccd0ff] text-[14px] px-3 py-1 rounded-[5px]">Heartfelt</span>
                                <span className="bg-[#ccd0ff] text-[14px] px-3 py-1 rounded-[5px]">Relatable</span>
                              </div>
                              
                              {/* Comments */}
                              <div className="space-y-3">
                                <div className="flex gap-3">
                                  <img alt="User" className="w-7 h-7 rounded-full" src={imgEllipse15} />
                                  <div className="flex-1">
                                                            <div className="font-medium text-[20px]">Comedy Lover</div>
                        <div className="text-[14px] text-gray-700">Your cultural insights are so refreshing and funny!</div>
                        
                        {/* Horizontal Line */}
                        <div className="border-t border-gray-200 my-2 w-full"></div>
                        
                        <div className="flex gap-2 mt-2">
                          <div className="bg-[#ebebea] h-[30px] w-[142px] rounded-[20px]"></div>
                          <img alt="Love" className="w-4 h-4" src={devIconLove2D} />
                          <img alt="Hot" className="w-4 h-4" src={fluentEmojiHotFace} />
                          <img alt="Smiley" className="w-4 h-4" src={imgStreamlineKameleonColorLoveSmiley} />
                        </div>
                                  </div>
                                </div>
                              </div>
                            </div>
                          </div>

                          {/* Post 6 - Marcus Johnson */}
                          <div className="bg-gray-50 rounded-[10px] p-4 border border-gray-200 w-[300px] flex-shrink-0">
                            {/* User Header */}
                            <div className="flex items-center mb-4">
                              <img alt="User avatar" className="w-[45px] h-[45px] rounded-full" src={imgEllipse17} />
                              <div className="ml-4">
                                <h3 className="font-semibold text-[16px]">Marcus Johnson</h3>
                                <div className="flex gap-2 mt-2">
                                  <button className="px-3 py-1 text-xs rounded-[5px] border border-gray-300 flex items-center bg-white">
                                    <svg className="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                                      <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                                    </svg>
                                    Follow
                                  </button>
                                  <button className="px-3 py-1 text-xs rounded-[5px] border border-gray-300 flex items-center bg-white">
                                    <svg className="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                                      <path d="M2.003 5.884L10 9.882l7.997-3.998A2 2 0 0016 4H4a2 2 0 00-1.997 1.884z" />
                                      <path d="M18 8.118l-8 4-8-4V14a2 2 0 002 2h12a2 2 0 002-2V8.118z" />
                                    </svg>
                                    Message
                                  </button>
                                </div>
                              </div>
                            </div>

                            {/* Post Image */}
                            <div className="w-full h-[197px] bg-cover bg-center rounded-[10px] mb-4" style={{ backgroundImage: `url('${imgImage6}')` }} />

                            {/* Post Content */}
                            <h3 className="font-semibold text-[20px] mb-2">Workplace Comedy Chronicles</h3>
                            <p className="text-[14px] mb-4 text-gray-700">Marcus turns office life into comedy gold with stories about meetings, coworkers, and corporate absurdity.</p>

                            {/* Tags */}
                            <div className="flex gap-2 mb-4">
                              <span className="text-[14px] text-gray-600">40 mins</span>
                              <span className="w-1.5 h-1.5 rounded-full bg-gray-400 self-center" />
                              <span className="text-[14px] text-gray-600">Workplace</span>
                              <span className="w-1.5 h-1.5 rounded-full bg-gray-400 self-center" />
                              <span className="text-[14px] text-gray-600">Corporate</span>
                            </div>

                                            {/* Engagement Stats */}
                <div className="flex items-center gap-6 text-[#979797]">
                  <div className="flex items-center gap-2">
                    <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M2 10.5a1.5 1.5 0 113 0v6a1.5 1.5 0 01-3 0v-6zM6 10.333v5.43a2 2 0 001.106 1.79l.05.025A4 4 0 008.943 18h5.416a2 2 0 001.962-1.608l1.2-6A2 2 0 0015.56 8H12V4a2 2 0 00-2-2 1 1 0 00-1 1v.667a4 4 0 01-.8 2.4L6.8 7.933a4 4 0 00-.8 2.4z" />
                    </svg>
                    <span>203</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M18 10c0 3.866-3.582 7-8 7a8.841 8.841 0 01-4.083-.98L2 17l1.338-3.123C2.493 12.767 2 11.434 2 10c0-3.866 3.582-7 8-7s8 3.134 8 7zM7 9H5v2h2V9zm8 0h-2v2h2V9zM9 9h2v2H9V9z" clipRule="evenodd" />
                    </svg>
                    <span>456</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M15 8a3 3 0 10-2.977-2.63l-4.94 2.47a3 3 0 100 4.319l4.94 2.47a3 3 0 10.895-1.789l-4.94-2.47a3.027 3.027 0 000-.74l4.94-2.47C13.456 7.68 14.19 8 15 8z" />
                    </svg>
                    <span>67</span>
                  </div>
                </div>

                {/* Horizontal Line */}
                <div className="border-t border-gray-200 my-4 w-full"></div>

                {/* Comment Section */}
                <div className="mt-4 pt-4 border-t border-gray-200">
                              <h4 className="text-[12px] font-medium mb-2 whitespace-nowrap">Comment Highlights:</h4>
                              <div className="flex gap-2 mb-3">
                                <span className="bg-[#ccd0ff] text-[14px] px-3 py-1 rounded-[5px]">Office Life</span>
                                <span className="bg-[#ccd0ff] text-[14px] px-3 py-1 rounded-[5px]">Too Real</span>
                                <span className="bg-[#ccd0ff] text-[14px] px-3 py-1 rounded-[5px]">Corporate Humor</span>
                              </div>
                              
                              {/* Comments */}
                              <div className="space-y-3">
                                <div className="flex gap-3">
                                  <img alt="User" className="w-7 h-7 rounded-full" src={imgEllipse13} />
                                  <div className="flex-1">
                                                            <div className="font-medium text-[20px]">Office Worker</div>
                        <div className="text-[14px] text-gray-700">This is exactly what happens in my office! Hilarious!</div>
                        
                        {/* Horizontal Line */}
                        <div className="border-t border-gray-200 my-2 w-full"></div>
                        
                        <div className="flex gap-2 mt-2">
                          <div className="bg-[#ebebea] h-[30px] w-[142px] rounded-[20px]"></div>
                          <img alt="Love" className="w-4 h-4" src={devIconLove2D} />
                          <img alt="Hot" className="w-4 h-4" src={fluentEmojiHotFace} />
                          <img alt="Smiley" className="w-4 h-4" src={imgStreamlineKameleonColorLoveSmiley} />
                        </div>
                                  </div>
                                </div>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Events Section */}
        <div className="bg-white rounded-xl p-6 border border-gray-200 shadow-sm">
          <h3 className="font-display text-lg font-semibold text-gray-900 mb-4">Laughter Live: Events Near You</h3>
          
          {/* Event Cards - Horizontal Scroll */}
          <div className="overflow-x-auto">
            <div className="flex gap-4 min-w-max">
              {/* Event 1 */}
              <div className="bg-gray-50 rounded-[10px] p-4 border border-gray-200 w-[320px] flex-shrink-0">
                {/* Event Image */}
                <div className="w-full h-[158px] bg-cover bg-center rounded-[10px] mb-4" style={{ backgroundImage: `url('${imgImage2}')` }} />
                
                {/* Event Title */}
                <h3 className="font-semibold text-[20px] mb-4">Laughter Unleashed Live !</h3>
                
                {/* Event Details - Structured Layout */}
                <div className="space-y-3 mb-4">
                                                      <div className="flex items-start gap-3">
                    <div className="flex-shrink-0 mt-0.5">
                      <svg className="w-4 h-4 text-blue-500" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z" clipRule="evenodd" />
                      </svg>
                    </div>
                    <div className="flex-1 min-w-0">
                      <span className="text-[14px] text-gray-700 block">Sat, Apr 20, 2025 at 8:00 PM</span>
                    </div>
                  </div>
                  
                  <div className="flex items-start gap-3">
                    <div className="flex-shrink-0 mt-0.5">
                      <svg className="w-4 h-4 text-blue-500" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M5.05 4.05a7 7 0 119.9 9.9L10 18.9l-4.95-4.95a7 7 0 010-9.9zM10 11a2 2 0 100-4 2 2 0 000 4z" clipRule="evenodd" />
                      </svg>
                    </div>
                    <div className="flex-1 min-w-0">
                      <span className="text-[14px] text-gray-700 block">Laugh Factory, Los Angeles</span>
                    </div>
                  </div>
                </div>
                
                {/* Status Badge */}
                <div className="flex justify-center mb-4">
                  <span className="bg-[#e8618c] text-white text-[12px] px-4 py-1 rounded-[20px]">Upcoming</span>
                </div>
                
                {/* Horizontal Line */}
                <div className="border-t border-gray-200 mb-4"></div>
                
                {/* Price and Actions */}
                <div className="flex items-center gap-3">
                  <div className="flex items-center gap-1">
                    <svg className="w-5 h-5 text-[#0d99ff]" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M8.433 7.418c.155-.103.346-.196.567-.267v1.698a2.305 2.305 0 01-.567-.267C8.07 8.34 8 8.114 8 8c0-.114.07-.34.433-.582zM11 12.849v-1.698c.22.071.412.164.567.267.364.243.433.468.433.582 0 .114-.07.34-.433.582a2.305 2.305 0 01-.567.267z" />
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-13a1 1 0 10-2 0v.092a4.535 4.535 0 00-1.676.662C6.602 6.234 6 7.009 6 8c0 .99.602 1.765 1.324 2.246.48.32 1.054.545 1.676.662v1.941c-.391-.127-.68-.317-.843-.504a1 1 0 10-1.51 1.31c.562.649 1.413 1.076 2.353 1.253V15a1 1 0 102 0v-.092a4.535 4.535 0 001.676-.662C13.398 13.766 14 12.991 14 12c0-.99-.602-1.765-1.324-2.246A4.535 4.535 0 0011 9.092V7.151c.391.127.68.317.843.504a1 1 0 101.511-1.31c-.563-.649-1.413-1.076-2.354-1.253V5z" clipRule="evenodd" />
                    </svg>
                    <span className="text-lg font-semibold text-[#0d99ff]">35</span>
                  </div>
                  
                  <button className="bg-[#0d99ff] text-white text-[14px] px-4 py-2 rounded-[5px] whitespace-nowrap">
                    Buy Tickets
                  </button>
                  
                  <button className="border border-[#0d99ff] text-[#0d99ff] text-[14px] px-4 py-2 rounded-[5px] whitespace-nowrap">
                    Add to Calendar
                  </button>
                </div>
              </div>

              {/* Event 2 */}
              <div className="bg-gray-50 rounded-[10px] p-4 border border-gray-200 w-[320px] flex-shrink-0">
                {/* Event Image */}
                <div className="w-full h-[158px] bg-cover bg-center rounded-[10px] mb-4" style={{ backgroundImage: `url('${imgImage3}')` }} />
                
                {/* Event Title */}
                <h3 className="font-semibold text-[20px] mb-4">Open Mic Night</h3>
                
                {/* Event Details - Structured Layout */}
                <div className="space-y-3 mb-4">
                                                      <div className="flex items-start gap-3">
                    <div className="flex-shrink-0 mt-0.5">
                      <svg className="w-4 h-4 text-blue-500" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z" clipRule="evenodd" />
                      </svg>
                    </div>
                    <div className="flex-1 min-w-0">
                      <span className="text-[14px] text-gray-700 block">Sun, Sep 8, 2025 at 7:00 PM</span>
                    </div>
                  </div>
                  
                  <div className="flex items-start gap-3">
                    <div className="flex-shrink-0 mt-0.5">
                      <svg className="w-4 h-4 text-blue-500" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M5.05 4.05a7 7 0 119.9 9.9L10 18.9l-4.95-4.95a7 7 0 010-9.9zM10 11a2 2 0 100-4 2 2 0 000 4z" clipRule="evenodd" />
                      </svg>
                    </div>
                    <div className="flex-1 min-w-0">
                      <span className="text-[14px] text-gray-700 block">Comedy Cellar, New York</span>
                    </div>
                  </div>
                </div>
                
                {/* Status Badge */}
                <div className="flex justify-center mb-4">
                  <span className="bg-[#e8618c] text-white text-[12px] px-4 py-1 rounded-[20px]">Live</span>
                </div>
                
                {/* Horizontal Line */}
                <div className="border-t border-gray-200 mb-4"></div>
                
                {/* Price and Actions */}
                <div className="flex items-center gap-3">
                  <div className="flex items-center gap-1">
                    <svg className="w-5 h-5 text-[#0d99ff]" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M8.433 7.418c.155-.103.346-.196.567-.267v1.698a2.305 2.305 0 01-.567-.267C8.07 8.34 8 8.114 8 8c0-.114.07-.34.433-.582zM11 12.849v-1.698c.22.071.412.164.567.267.364.243.433.468.433.582 0 .114-.07.34-.433.582a2.305 2.305 0 01-.567.267z" />
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-13a1 1 0 10-2 0v.092a4.535 4.535 0 00-1.676.662C6.602 6.234 6 7.009 6 8c0 .99.602 1.765 1.324 2.246.48.32 1.054.545 1.676.662v1.941c-.391-.127-.68-.317-.843-.504a1 1 0 10-1.51 1.31c.562.649 1.413 1.076 2.353 1.253V15a1 1 0 102 0v-.092a4.535 4.535 0 001.676-.662C13.398 13.766 14 12.991 14 12c0-.99-.602-1.765-1.324-2.246A4.535 4.535 0 0011 9.092V7.151c.391.127.68.317.843.504a1 1 0 101.511-1.31c-.563-.649-1.413-1.076-2.354-1.253V5z" clipRule="evenodd" />
                    </svg>
                    <span className="text-lg font-semibold text-[#0d99ff]">Free</span>
                  </div>
                  
                  <button className="bg-[#0d99ff] text-white text-[14px] px-4 py-2 rounded-[5px] whitespace-nowrap">
                    Buy Tickets
                  </button>
                  
                  <button className="border border-[#0d99ff] text-[#0d99ff] text-[14px] px-4 py-2 rounded-[5px] whitespace-nowrap">
                    Add to Calendar
                  </button>
                </div>
              </div>

              {/* Event 3 */}
              <div className="bg-gray-50 rounded-[10px] p-4 border border-gray-200 w-[320px] flex-shrink-0">
                {/* Event Image */}
                <div className="w-full h-[158px] bg-cover bg-center rounded-[10px] mb-4" style={{ backgroundImage: `url('${imgImage4}')` }} />
                
                {/* Event Title */}
                <h3 className="font-semibold text-[20px] mb-4">Stand - Up Showcase</h3>
                
                {/* Event Details - Structured Layout */}
                <div className="space-y-3 mb-4">
                                                      <div className="flex items-start gap-3">
                    <div className="flex-shrink-0 mt-0.5">
                      <svg className="w-4 h-4 text-blue-500" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z" clipRule="evenodd" />
                      </svg>
                    </div>
                    <div className="flex-1 min-w-0">
                      <span className="text-[14px] text-gray-700 block">Mon, Oct 26, 2026 at 4:00 PM</span>
                    </div>
                  </div>
                  
                  <div className="flex items-start gap-3">
                    <div className="flex-shrink-0 mt-0.5">
                      <svg className="w-4 h-4 text-blue-500" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M5.05 4.05a7 7 0 119.9 9.9L10 18.9l-4.95-4.95a7 7 0 010-9.9zM10 11a2 2 0 100-4 2 2 0 000 4z" clipRule="evenodd" />
                      </svg>
                    </div>
                    <div className="flex-1 min-w-0">
                      <span className="text-[14px] text-gray-700 block">Second City, Chicago</span>
                    </div>
                  </div>
                </div>
                
                {/* Status Badge */}
                <div className="flex justify-center mb-4">
                  <span className="bg-[#e8618c] text-white text-[12px] px-4 py-1 rounded-[20px]">Upcoming</span>
                </div>
                
                {/* Horizontal Line */}
                <div className="border-t border-gray-200 mb-4"></div>
                
                {/* Price and Actions */}
                <div className="flex items-center gap-3">
                  <div className="flex items-center gap-1">
                    <svg className="w-5 h-5 text-[#0d99ff]" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M8.433 7.418c.155-.103.346-.196.567-.267v1.698a2.305 2.305 0 01-.567-.267C8.07 8.34 8 8.114 8 8c0-.114.07-.34.433-.582zM11 12.849v-1.698c.22.071.412.164.567.267.364.243.433.468.433.582 0 .114-.07.34-.433.582a2.305 2.305 0 01-.567.267z" />
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-13a1 1 0 10-2 0v.092a4.535 4.535 0 00-1.676.662C6.602 6.234 6 7.009 6 8c0 .99.602 1.765 1.324 2.246.48.32 1.054.545 1.676.662v1.941c-.391-.127-.68-.317-.843-.504a1 1 0 10-1.51 1.31c.562.649 1.413 1.076 2.353 1.253V15a1 1 0 102 0v-.092a4.535 4.535 0 001.676-.662C13.398 13.766 14 12.991 14 12c0-.99-.602-1.765-1.324-2.246A4.535 4.535 0 0011 9.092V7.151c.391.127.68.317.843.504a1 1 0 101.511-1.31c-.563-.649-1.413-1.076-2.354-1.253V5z" clipRule="evenodd" />
                    </svg>
                    <span className="text-lg font-semibold text-[#0d99ff]">35</span>
                  </div>
                  
                  <button className="bg-[#0d99ff] text-white text-[14px] px-4 py-2 rounded-[5px] whitespace-nowrap">
                    Buy Tickets
                  </button>
                  
                  <button className="border border-[#0d99ff] text-[#0d99ff] text-[14px] px-4 py-2 rounded-[5px] whitespace-nowrap">
                    Add to Calendar
                  </button>
                </div>
              </div>

              {/* Event 4 */}
              <div className="bg-gray-50 rounded-[10px] p-4 border border-gray-200 w-[320px] flex-shrink-0">
                {/* Event Image */}
                <div className="w-full h-[158px] bg-cover bg-center rounded-[10px] mb-4" style={{ backgroundImage: `url('${imgImage2}')` }} />
                
                {/* Event Title */}
                <h3 className="font-semibold text-[20px] mb-4">Comedy Night Extravaganza</h3>
                
                {/* Event Details - Structured Layout */}
                <div className="space-y-3 mb-4">
                  <div className="flex items-start gap-3">
                    <div className="flex-shrink-0 mt-0.5">
                      <svg className="w-4 h-4 text-blue-500" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z" clipRule="evenodd" />
                      </svg>
                    </div>
                    <div className="flex-1 min-w-0">
                      <span className="text-[14px] text-gray-700 block">Fri, Dec 15, 2025 at 9:30 PM</span>
                    </div>
                  </div>
                  
                  <div className="flex items-start gap-3">
                    <div className="flex-shrink-0 mt-0.5">
                      <svg className="w-4 h-4 text-blue-500" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M5.05 4.05a7 7 0 119.9 9.9L10 18.9l-4.95-4.95a7 7 0 010-9.9zM10 11a2 2 0 100-4 2 2 0 000 4z" clipRule="evenodd" />
                      </svg>
                    </div>
                    <div className="flex-1 min-w-0">
                      <span className="text-[14px] text-gray-700 block">The Improv, Miami</span>
                    </div>
                  </div>
                </div>
                
                {/* Status Badge */}
                <div className="flex justify-center mb-4">
                  <span className="bg-[#e8618c] text-white text-[12px] px-4 py-1 rounded-[20px]">Upcoming</span>
                </div>
                
                {/* Horizontal Line */}
                <div className="border-t border-gray-200 mb-4"></div>
                
                {/* Price and Actions */}
                <div className="flex items-center gap-3">
                  <div className="flex items-center gap-1">
                    <svg className="w-5 h-5 text-[#0d99ff]" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M8.433 7.418c.155-.103.346-.196.567-.267v1.698a2.305 2.305 0 01-.567-.267C8.07 8.34 8 8.114 8 8c0-.114.07-.34.433-.582zM11 12.849v-1.698c.22.071.412.164.567.267.364.243.433.468.433.582 0 .114-.07.34-.433.582a2.305 2.305 0 01-.567.267z" />
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-13a1 1 0 10-2 0v.092a4.535 4.535 0 00-1.676.662C6.602 6.234 6 7.009 6 8c0 .99.602 1.765 1.324 2.246.48.32 1.054.545 1.676.662v1.941c-.391-.127-.68-.317-.843-.504a1 1 0 10-1.51 1.31c.562.649 1.413 1.076 2.353 1.253V15a1 1 0 102 0v-.092a4.535 4.535 0 001.676-.662C13.398 13.766 14 12.991 14 12c0-.99-.602-1.765-1.324-2.246A4.535 4.535 0 0011 9.092V7.151c.391.127.68.317.843.504a1 1 0 101.511-1.31c-.563-.649-1.413-1.076-2.354-1.253V5z" clipRule="evenodd" />
                    </svg>
                    <span className="text-lg font-semibold text-[#0d99ff]">45</span>
                  </div>
                  
                  <button className="bg-[#0d99ff] text-white text-[14px] px-4 py-2 rounded-[5px] whitespace-nowrap">
                    Buy Tickets
                  </button>
                  
                  <button className="border border-[#0d99ff] text-[#0d99ff] text-[14px] px-4 py-2 rounded-[5px] whitespace-nowrap">
                    Add to Calendar
                  </button>
                </div>
              </div>

              {/* Event 5 */}
              <div className="bg-gray-50 rounded-[10px] p-4 border border-gray-200 w-[320px] flex-shrink-0">
                {/* Event Image */}
                <div className="w-full h-[158px] bg-cover bg-center rounded-[10px] mb-4" style={{ backgroundImage: `url('${imgImage3}')` }} />
                
                {/* Event Title */}
                <h3 className="font-semibold text-[20px] mb-4">Late Night Laughs</h3>
                
                {/* Event Details - Structured Layout */}
                <div className="space-y-3 mb-4">
                  <div className="flex items-start gap-3">
                    <div className="flex-shrink-0 mt-0.5">
                      <svg className="w-4 h-4 text-blue-500" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z" clipRule="evenodd" />
                      </svg>
                    </div>
                    <div className="flex-1 min-w-0">
                      <span className="text-[14px] text-gray-700 block">Wed, Jan 8, 2026 at 11:00 PM</span>
                    </div>
                  </div>
                  
                  <div className="flex items-start gap-3">
                    <div className="flex-shrink-0 mt-0.5">
                      <svg className="w-4 h-4 text-blue-500" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M5.05 4.05a7 7 0 119.9 9.9L10 18.9l-4.95-4.95a7 7 0 010-9.9zM10 11a2 2 0 100-4 2 2 0 000 4z" clipRule="evenodd" />
                      </svg>
                    </div>
                    <div className="flex-1 min-w-0">
                      <span className="text-[14px] text-gray-700 block">Comedy Underground, Seattle</span>
                    </div>
                  </div>
                </div>
                
                {/* Status Badge */}
                <div className="flex justify-center mb-4">
                  <span className="bg-[#e8618c] text-white text-[12px] px-4 py-1 rounded-[20px]">Live</span>
                </div>
                
                {/* Horizontal Line */}
                <div className="border-t border-gray-200 mb-4"></div>
                
                {/* Price and Actions */}
                <div className="flex items-center gap-3">
                  <div className="flex items-center gap-1">
                    <svg className="w-5 h-5 text-[#0d99ff]" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M8.433 7.418c.155-.103.346-.196.567-.267v1.698a2.305 2.305 0 01-.567-.267C8.07 8.34 8 8.114 8 8c0-.114.07-.34.433-.582zM11 12.849v-1.698c.22.071.412.164.567.267.364.243.433.468.433.582 0 .114-.07.34-.433.582a2.305 2.305 0 01-.567.267z" />
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-13a1 1 0 10-2 0v.092a4.535 4.535 0 00-1.676.662C6.602 6.234 6 7.009 6 8c0 .99.602 1.765 1.324 2.246.48.32 1.054.545 1.676.662v1.941c-.391-.127-.68-.317-.843-.504a1 1 0 10-1.51 1.31c.562.649 1.413 1.076 2.353 1.253V15a1 1 0 102 0v-.092a4.535 4.535 0 001.676-.662C13.398 13.766 14 12.991 14 12c0-.99-.602-1.765-1.324-2.246A4.535 4.535 0 0011 9.092V7.151c.391.127.68.317.843.504a1 1 0 101.511-1.31c-.563-.649-1.413-1.076-2.354-1.253V5z" clipRule="evenodd" />
                    </svg>
                    <span className="text-lg font-semibold text-[#0d99ff]">Free</span>
                  </div>
                  
                  <button className="bg-[#0d99ff] text-white text-[14px] px-4 py-2 rounded-[5px] whitespace-nowrap">
                    Buy Tickets
                  </button>
                  
                  <button className="border border-[#0d99ff] text-[#0d99ff] text-[14px] px-4 py-2 rounded-[5px] whitespace-nowrap">
                    Add to Calendar
                  </button>
                </div>
              </div>

              {/* Event 6 */}
              <div className="bg-gray-50 rounded-[10px] p-4 border border-gray-200 w-[320px] flex-shrink-0">
                {/* Event Image */}
                <div className="w-full h-[158px] bg-cover bg-center rounded-[10px] mb-4" style={{ backgroundImage: `url('${imgImage4}')` }} />
                
                {/* Event Title */}
                <h3 className="font-semibold text-[20px] mb-4">Weekend Comedy Festival</h3>
                
                {/* Event Details - Structured Layout */}
                <div className="space-y-3 mb-4">
                  <div className="flex items-start gap-3">
                    <div className="flex-shrink-0 mt-0.5">
                      <svg className="w-4 h-4 text-blue-500" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z" clipRule="evenodd" />
                      </svg>
                    </div>
                    <div className="flex-1 min-w-0">
                      <span className="text-[14px] text-gray-700 block">Sat, Feb 14, 2026 at 6:00 PM</span>
                    </div>
                  </div>
                  
                  <div className="flex items-start gap-3">
                    <div className="flex-shrink-0 mt-0.5">
                      <svg className="w-4 h-4 text-blue-500" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M5.05 4.05a7 7 0 119.9 9.9L10 18.9l-4.95-4.95a7 7 0 010-9.9zM10 11a2 2 0 100-4 2 2 0 000 4z" clipRule="evenodd" />
                      </svg>
                    </div>
                    <div className="flex-1 min-w-0">
                      <span className="text-[14px] text-gray-700 block">Zanies Comedy Club, Nashville</span>
                    </div>
                  </div>
                </div>
                
                {/* Status Badge */}
                <div className="flex justify-center mb-4">
                  <span className="bg-[#e8618c] text-white text-[12px] px-4 py-1 rounded-[20px]">Upcoming</span>
                </div>
                
                {/* Horizontal Line */}
                <div className="border-t border-gray-200 mb-4"></div>
                
                {/* Price and Actions */}
                <div className="flex items-center gap-3">
                  <div className="flex items-center gap-1">
                    <svg className="w-5 h-5 text-[#0d99ff]" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M8.433 7.418c.155-.103.346-.196.567-.267v1.698a2.305 2.305 0 01-.567-.267C8.07 8.34 8 8.114 8 8c0-.114.07-.34.433-.582zM11 12.849v-1.698c.22.071.412.164.567.267.364.243.433.468.433.582 0 .114-.07.34-.433.582a2.305 2.305 0 01-.567.267z" />
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-13a1 1 0 10-2 0v.092a4.535 4.535 0 00-1.676.662C6.602 6.234 6 7.009 6 8c0 .99.602 1.765 1.324 2.246.48.32 1.054.545 1.676.662v1.941c-.391-.127-.68-.317-.843-.504a1 1 0 10-1.51 1.31c.562.649 1.413 1.076 2.353 1.253V15a1 1 0 102 0v-.092a4.535 4.535 0 001.676-.662C13.398 13.766 14 12.991 14 12c0-.99-.602-1.765-1.324-2.246A4.535 4.535 0 0011 9.092V7.151c.391.127.68.317.843.504a1 1 0 101.511-1.31c-.563-.649-1.413-1.076-2.354-1.253V5z" clipRule="evenodd" />
                    </svg>
                    <span className="text-lg font-semibold text-[#0d99ff]">55</span>
                  </div>
                  
                  <button className="bg-[#0d99ff] text-white text-[14px] px-4 py-2 rounded-[5px] whitespace-nowrap">
                    Buy Tickets
                  </button>
                  
                  <button className="border border-[#0d99ff] text-[#0d99ff] text-[14px] px-4 py-2 rounded-[5px] whitespace-nowrap">
                    Add to Calendar
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Join Groups Section */}
        <div className="bg-white rounded-xl p-6 border border-gray-200 shadow-sm">
          <h3 className="font-display text-lg font-semibold text-gray-900 mb-4">Join Stand-up Groups</h3>
          <p className="text-[14px] mb-6 text-gray-700">Connect with fellow comedy enthusiasts and performers. Share Jokes, plan meetups, and find your next open mic.</p>
          <button className="bg-[#636ae8] text-white text-[14px] px-6 py-2 rounded-md hover:bg-[#5a61d9] transition-colors">Browse Groups</button>
        </div>
      </main>

      {/* Bottom Navigation */}
      <BottomNav onNavigate={onNavigate} currentView="community" />
    </div>
  );
};

export default CommunityHub;