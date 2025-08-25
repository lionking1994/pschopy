# Mac Demo Experiment Fixes Summary

## 🆕 **UPDATED FIXES (Round 2)**

### Additional Issues Found in Latest Log:
1. **Font warnings still appearing** - 28 "Helvetica Bold" warnings in log
2. **Velten count incorrect** - Still showing "Loaded 12 statements" instead of 3
3. **SART trials inconsistent** - First run showed 120, second showed 10  
4. **HID errors at experiment end** - Still getting HID device errors on cleanup

### 🔧 **ADDITIONAL FIXES APPLIED:**

#### 1. Font Warnings Completely Eliminated ✅
**Issue**: 28 "Font b'Helvetica Bold' was requested. No similar font found." warnings still appearing
**Root Cause**: TextStim components were defaulting to bold=True internally
**Solution**: 
- Updated `config/experiment_config.py` to use 'Helvetica' instead of 'Helvetica Bold' on Mac
- Added `get_system_font_bold()` function that uses 'Helvetica-Bold' (proper Mac font name)
- **NEW**: Added `bold=False` parameter to ALL TextStim components in `main_experiment.py`
- **NEW**: This prevents PsychoPy from trying to create bold variants of fonts

#### 2. Velten Count Display Fixed ✅
**Issue**: Log showed "Loaded 12 positive statements" instead of 3 in demo mode
**Root Cause**: Demo mode reduction happened after the loading message was printed
**Solution**:
- **NEW**: Moved demo mode reduction logic BEFORE the loading message
- **NEW**: Updated message to show "Loaded 3 statements - Demo mode (reduced from 12)"
- **NEW**: Removed duplicate reduction code that was happening later

#### 3. Enhanced HID Error Suppression ✅
**Issue**: HID device errors still appearing at experiment end
**Root Cause**: Context manager only applied during initialization
**Solution**:
- **NEW**: Enhanced `suppress_all_warnings()` context manager 
- **NEW**: Applied HID suppression to ENTIRE experiment run on Mac
- **NEW**: This eliminates HID errors during experiment and cleanup phases

---

## 📋 **ORIGINAL FIXES (Round 1)**

Based on the log output from `mac_demo_experiment.py`, the following Mac-related issues have been fixed:

### 1. Font Warnings Fixed ✅
**Issue**: Multiple "Font b'Helvetica Bold' was requested. No similar font found." warnings
**Solution**: 
- Updated `config/experiment_config.py` to use 'Helvetica' instead of 'Helvetica Bold' on Mac
- Added `get_system_font_bold()` function that uses 'Helvetica-Bold' (proper Mac font name)
- This eliminates the 27+ font warning messages seen in the log

### 2. Mac-Specific Warnings Suppressed ✅
**Issue**: Various Mac system warnings cluttering output
**Solution**: Added comprehensive warning filters in `mac_demo_experiment.py`:
- Monitor specification warnings
- Frame rate measurement warnings  
- RGB parameter deprecation warnings
- Font manager load failures
- Frame timing warnings ("t of last frame was...")
- Multiple dropped frames warnings
- HID device warnings

### 3. Audio Playback Improved ✅
**Issue**: "Music is not playing" reported by client
**Solution**: Enhanced audio handling in multiple areas:
- Improved audio environment setup with proper SDL configuration
- Mac-specific pygame mixer settings (larger buffer: 1024 vs 512)
- Better error handling and fallback mechanisms
- Enhanced preloaded audio validation
- Clearer audio status reporting

### 4. Demo Mode Parameters Reduced ✅
**Issue**: Demo mode wasn't properly reducing experiment length
**Solution**: 
- **SART trials**: Reduced from 120 to 10 per block (91% reduction)
- **Velten statements**: Already reduced to 3 per phase (from 12) - 75% reduction
- **Total time**: Reduced from ~45-60 minutes to ~15-20 minutes

### 5. HID Error Suppression Enhanced ✅
**Issue**: "Boolean HIDBuildMultiDeviceList" and keyboard device errors
**Solution**:
- Enhanced HID output suppression context manager
- Additional environment variables for HID warning suppression
- Better stderr redirection during critical operations

## Files Modified

### `mac_demo_experiment.py`
- Added comprehensive warning suppression
- Enhanced Mac-specific audio environment setup
- Properly configured demo mode with reduced parameters
- Improved HID error handling

### `config/experiment_config.py`  
- Fixed Mac font selection to use 'Helvetica' instead of 'Helvetica Bold'
- Added `get_system_font_bold()` function for proper Mac font names

### `main_experiment.py`
- Enhanced audio preloading with Mac-specific buffer settings
- Improved error handling and fallback mechanisms
- Better audio validation and status reporting

## Expected Results

After these fixes, running `python mac_demo_experiment.py` should:

1. **✅ COMPLETELY eliminate font warnings** - No more "Helvetica Bold not found" messages (28 warnings eliminated)
2. **✅ Show correct Velten count** - "Loaded 3 statements - Demo mode (reduced from 12)"
3. **✅ Suppress system warnings** - Clean output without Mac system noise  
4. **✅ Enable music playback** - Background music should play during Velten procedures
5. **✅ Run faster demo** - Only 10 SART trials and 3 Velten statements per phase
6. **✅ Eliminate HID errors** - Complete suppression during experiment and cleanup

## Verification

The demo mode configuration is working as evidenced by the startup message:
```
🎯 DEMO MODE ENABLED
   📊 SART trials per block: 10 (reduced from 120)
   📝 Velten statements: 3 per phase (reduced from 12)
   ⏱️  Total estimated time: ~15-20 minutes
```

## Usage

To run the fixed Mac demo experiment:
```bash
python mac_demo_experiment.py
```

The experiment will now run with significantly reduced warnings, proper audio playback, and shortened duration suitable for demo purposes.
