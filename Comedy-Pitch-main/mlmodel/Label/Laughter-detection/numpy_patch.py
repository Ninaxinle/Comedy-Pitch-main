#!/usr/bin/env python3
"""
NumPy Compatibility Patch for librosa

This patch fixes the np.complex deprecation issue that occurs with newer numpy versions.
Must be imported BEFORE importing librosa.
"""

import numpy as np

# Fix for np.complex deprecation in librosa
if not hasattr(np, 'complex'):
    np.complex = complex

# Fix for other potential deprecation issues
if not hasattr(np, 'float'):
    np.float = float

if not hasattr(np, 'int'):
    np.int = int

print("NumPy compatibility patch applied")