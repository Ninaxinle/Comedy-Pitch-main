// Global error handler for VSC-related errors
export const setupErrorHandler = () => {
  // Handle unhandled promise rejections
  window.addEventListener('unhandledrejection', (event) => {
    const error = event.reason;
    
    // Check if it's a VSC-related error
    if (error && error.message && (
      error.message.includes('VSC.inIframe') ||
      error.message.includes('event-manager.js') ||
      error.message.includes('window.VSC')
    )) {
      console.warn('VSC API not available, continuing without VS Code integration');
      event.preventDefault(); // Prevent the error from being logged
      return;
    }
    
    // Log other errors normally
    console.error('Unhandled promise rejection:', error);
  });

  // Handle regular errors
  window.addEventListener('error', (event) => {
    const error = event.error;
    
    // Check if it's a VSC-related error
    if (error && error.message && (
      error.message.includes('VSC.inIframe') ||
      error.message.includes('event-manager.js') ||
      error.message.includes('window.VSC')
    )) {
      console.warn('VSC API not available, continuing without VS Code integration');
      event.preventDefault(); // Prevent the error from being logged
      return;
    }
    
    // Log other errors normally
    console.error('Global error:', error);
  });

  // Additional protection: Override window.VSC if it doesn't exist
  if (typeof window !== 'undefined' && !window.VSC) {
    Object.defineProperty(window, 'VSC', {
      value: {
        inIframe: () => false,
        getState: () => ({}),
        setState: () => {},
        postMessage: () => {}
      },
      writable: false,
      configurable: false
    });
  }
};

// Safe VSC API wrapper
export const safeVSC = {
  inIframe(): boolean {
    try {
      if (typeof window !== 'undefined' && 
          window.VSC && 
          typeof window.VSC.inIframe === 'function') {
        return window.VSC.inIframe();
      }
      return false;
    } catch (e) {
      return false;
    }
  },
  
  getTopDocument(): Document | null {
    try {
      if (this.inIframe() && window.top) {
        return window.top.document;
      }
      return document;
    } catch (e) {
      return document;
    }
  }
}; 