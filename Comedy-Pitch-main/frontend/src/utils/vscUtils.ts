// Utility functions for VS Code webview integration
export const vscUtils = {
  /**
   * Safely check if we're running in a VS Code iframe
   */
  inIframe(): boolean {
    try {
      // Check if VSC API exists and has the inIframe method
      if (typeof window !== 'undefined' && 
          window.VSC && 
          typeof window.VSC.inIframe === 'function') {
        const result = window.VSC.inIframe();
        return typeof result === 'boolean' ? result : false;
      }
      
      // Fallback: check if we're in an iframe
      return window !== window.top;
    } catch (e) {
      // Cross-origin iframe or other error - assume we're not in VSC iframe
      return false;
    }
  },

  /**
   * Safely get the top document if possible
   */
  getTopDocument(): Document | null {
    try {
      if (this.inIframe() && window.top) {
        return window.top.document;
      }
      return document;
    } catch (e) {
      // Cross-origin iframe - return current document
      return document;
    }
  },

  /**
   * Check if VSC API is available
   */
  isVSCAvailable(): boolean {
        return !!(typeof window !== 'undefined' &&
            window.VSC && 
            typeof window.VSC === 'object');
  }
};

// Extend Window interface to include VSC
declare global {
  interface Window {
    VSC?: {
      inIframe?: () => boolean;
      getState?: () => any;
      setState?: (state: any) => void;
      postMessage?: (message: any) => void;
      [key: string]: any;
    };
  }
} 