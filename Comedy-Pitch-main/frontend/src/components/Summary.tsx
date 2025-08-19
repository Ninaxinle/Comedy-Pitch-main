import React from 'react';

interface SummaryProps {
  onNavigate: (destination: string, params?: { [key: string]: any }) => void;
}

const Summary: React.FC<SummaryProps> = ({ onNavigate }) => {
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-end z-50 animate-fadeIn">
      <div className="bg-white w-full min-h-[90vh] shadow-xl mx-auto rounded-t-xl overflow-hidden animate-slideUp">
        {/* Main Content */}
        <main className="flex-grow overflow-y-auto p-4 space-y-6 pb-24 max-h-[calc(100vh-200px)]">
          {/* Score Card */}
          <div className="bg-white rounded-xl p-6 border border-gray-200 shadow-sm">
            <div className="flex justify-center">
              <div className="bg-[#fde12d] w-[239px] h-[100px] rounded-[20px] flex items-center justify-center">
                <span className="font-semibold text-[60px] text-[#0d0c0c]">3.8</span>
              </div>
            </div>
          </div>

          {/* Performance Details */}
          <div className="bg-white rounded-xl p-6 border border-gray-200 shadow-sm">
            <h3 className="font-display text-lg font-semibold text-gray-900 mb-4">Performance Details</h3>
            <div className="space-y-4">
              <div className="flex justify-between items-start">
                <div className="text-lg">
                  <span className="font-medium">Title:</span> Married Life
                </div>
                <div className="text-lg">
                  <span className="font-medium">Date:</span> 12/25/2025
                </div>
              </div>
              
              <div>
                <div className="font-medium text-lg mb-2">Brief Description:</div>
                <p className="text-gray-800 leading-relaxed">
                  A lighthearted bit that playfully pokes fun at the sweet yet frustrating moments of married life.
                </p>
              </div>
            </div>
          </div>

          {/* Summary Section */}
          <div className="bg-white rounded-xl p-6 border border-gray-200 shadow-sm">
            <h3 className="font-display text-lg font-semibold text-gray-900 mb-4">Summary & Suggestions</h3>
            <p className="text-gray-800 leading-relaxed">
              This marriage-themed stand-up has great potential—the topic is familiar and easy for audiences to connect with. 
              Your delivery felt confident and naturally smooth, especially impressive for something improvised. To make the 
              humor land even harder, you could add sharper punchlines or unexpected twists that catch people off guard. 
              Tightening some of the pacing would help keep the audience fully engaged, and using callbacks or linking 
              earlier jokes to later ones could give the set a stronger structure. Overall, it's a solid starting point, 
              and with a bit of polishing, it could work brilliantly in a live performance.
            </p>
          </div>

          {/* Action Buttons */}
          <div className="fixed bottom-6 left-0 right-0 px-6 flex justify-between">
            <button 
              onClick={() => onNavigate('analysis', { videoTitle: 'Married Life' })}
              className="bg-[#636ae8] text-white font-bold text-xl py-3 px-8 rounded-lg w-[103px]"
            >
              Save
            </button>
            <div className="bg-white rounded-xl p-4 border border-gray-200 shadow-sm flex items-center justify-center">
              <button 
                onClick={() => onNavigate('voice-recorder')}
                className="border border-[#979797] text-[#636ae8] font-bold text-xl py-3 px-8 rounded-lg w-[103px]"
              >
                Discard
              </button>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
};

export default Summary;