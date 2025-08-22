# PsychoPy Mood Induction + SART Experiment

A comprehensive PsychoPy experiment combining mood induction procedures with a Sustained Attention to Response Task (SART) for studying mind-wandering and attention.

## ✅ **Ready to Use - No Setup Required!**

This experiment is **fully functional** and uses modern PsychoPy components with keyboard-based input for maximum compatibility.

## 🚀 **Quick Start**

### **Run the Experiment:**

**Full Experiment (45-60 minutes):**
```bash
python main_experiment.py
```

**Demo Mode (20-25 minutes):**
```bash
python demo_experiment.py
```
*Shortened version with 10 trials per SART block and 3 Velten statements per phase*

### **Install Dependencies (if needed):**
```bash
pip install -r requirements.txt
```

## 📋 **Project Structure**

```
psychopy/
├── main_experiment.py              # ✅ Main experiment (WORKING VERSION)
├── main_experiment_working.py      # Backup copy
├── config/
│   └── experiment_config.py        # All experimental parameters
├── scripts/
│   ├── video_preloader.py          # Video loading optimization
│   ├── data_analyzer.py            # Data analysis tools
│   └── test_core_functionality.py  # Core logic tests
├── tests/
│   ├── test_rating_scales.py       # Modern rating scale tests
│   └── test_psychopy_gui.py        # GUI functionality tests
├── stimuli/
│   ├── videos/                     # Video clips (add your files here)
│   ├── audio/                      # Background music (add your files here)
│   └── velten_statements/          # Text files with statements
├── data/                           # Experiment data (auto-generated)
├── requirements.txt                # Python dependencies
├── setup.py                       # Automated setup script
└── README.md                      # This file
```

## 🎮 **How to Use**

### **Participant Input Methods:**
- **Email Entry**: Type email address and press ENTER
- **Condition Selection**: Press keys 1-4 for counterbalancing conditions
- **Mood Ratings**: Press keys 1-9 (1=Very Negative, 9=Very Positive)
- **Velten Ratings**: Press keys 1-7 (1=Not at all, 7=Completely)
- **Mind-Wandering Probes**: Press keys 1-7 (1=Not at all, 7=Very much)
- **SART Responses**: Use LEFT/RIGHT arrow keys
- **Exit Anytime**: Press ESCAPE key

### **Experiment Flow:**
1. **Participant Setup** - Email and condition entry
2. **Video Preloading** - Loading screen with progress
3. **Baseline Mood Rating** - Initial mood assessment
4. **Mood Induction** - Velten statements + music OR video clips
5. **Post-Induction Mood** - Mood assessment after induction
6. **SART Task** - Sustained attention task with response inhibition
7. **Mind-Wandering Probes** - Appear during SART blocks (FIXED)
8. **Data Export** - Automatic CSV file generation

## 🔧 **Features**

### **✅ All Issues Fixed:**
- **Probe Timing**: Mind-wandering probes appear DURING SART blocks
- **Audio Playback**: Music plays properly during Velten statements
- **Video Loading**: Preloading system eliminates delays
- **Modern Components**: Uses Slider instead of legacy RatingScale
- **GUI Compatibility**: Keyboard input avoids dialog issues

### **Experimental Components:**
- **4 Counterbalancing Conditions** - Fully implemented
- **Mood Induction Methods**: Velten statements + music, Video clips
- **SART Task**: Response inhibition and non-inhibition blocks
- **Mind-Wandering Assessment**: TUT and FMT probes
- **Comprehensive Data Collection**: All variables exported to CSV

### **Technical Features:**
- **Modern PsychoPy 2025.1.1** compatibility
- **PyQt6 GUI backend** support
- **Keyboard-based interface** (no problematic dialogs)
- **Video preloading system** for smooth playback
- **Robust error handling** and fallbacks
- **Professional data export** with timestamps

## 📊 **Data Collection**

### **Output Variables:**
- Participant information (email, code, condition)
- Session timing and timestamps
- Mood ratings (1-9 scale)
- Velten statement ratings (1-7 scale)
- SART trial data (stimulus, response, accuracy, RT)
- Mind-wandering probe responses (TUT and FMT ratings)
- Media file information (video/audio played)

### **File Format:**
Data is automatically saved as CSV files in the `data/` directory with format:
`participant_MOOD_SART_[code]_[timestamp].csv`

## 🧪 **Testing**

### **Run Tests:**
```bash
# Test core functionality (no GUI required)
python scripts/test_core_functionality.py

# Test modern rating scales
python tests/test_rating_scales.py

# Test GUI components (requires display)
python tests/test_psychopy_gui.py
```

### **Analyze Data:**
```bash
# Generate sample data for testing
python scripts/create_sample_data.py

# Analyze experiment data
python scripts/data_analyzer.py --help
```

## 🎯 **Counterbalancing**

Four conditions are implemented as specified:

| Condition | SART Order | Mood Inductions | Mood Repair |
|-----------|------------|-----------------|-------------|
| 1 | RI-NRI-RI-NRI | V+, V+, M-, M- | No |
| 2 | RI-NRI-RI-NRI | M-, M-, V+, V+ | Yes |
| 3 | NRI-RI-NRI-RI | V-, V-, M+, M+ | Yes |
| 4 | NRI-RI-NRI-RI | M+, M+, V-, V- | No |

**Legend:**
- RI = Response Inhibition, NRI = Non-Response Inhibition
- V = Velten + Music, M = Movie/Video
- +/- = Positive/Negative valence

## 📦 **Installation**

### **Automatic Setup:**
```bash
python setup.py
```

### **Manual Installation:**
```bash
# Install Python dependencies
pip install -r requirements.txt

# For headless environments, install system dependencies:
sudo apt install build-essential libgtk-3-dev libwebkit2gtk-4.0-dev
```

### **Add Your Media Files:**
1. **Videos**: Add `.mp4` files to `stimuli/videos/`
   - `positive_clip1.mp4`, `positive_clip2.mp4`
   - `negative_clip.mp4`, `neutral_clip.mp4`, `mood_repair.mp4`

2. **Audio**: Add `.wav` files to `stimuli/audio/`
   - `positive_music.wav`, `negative_music.wav`

3. **Statements**: Text files are auto-generated in `stimuli/velten_statements/`
   - Customize `positive_statements.txt` and `negative_statements.txt` as needed

## 🔧 **Configuration**

All experimental parameters can be modified in `config/experiment_config.py`:

- **Timing parameters** (stimulus duration, ISI, etc.)
- **SART settings** (trials per block, target digit)
- **Rating scales** (ranges, labels)
- **File paths** (stimuli locations)
- **Display settings** (screen size, colors)

## ✅ **System Requirements**

- **Python 3.8+**
- **PsychoPy 2025.1.1+**
- **PyQt6 6.9.0+** (for GUI support)
- **Modern display** (1920x1080 recommended)
- **Audio output** (for music playback)
- **Keyboard input** (arrow keys + number keys)

## 🏆 **Status: Production Ready**

This experiment is **fully functional** and ready for:
- ✅ **Pilot studies** and data collection
- ✅ **Laboratory deployment** 
- ✅ **Research use** with participants
- ✅ **Data analysis** and publication

## 📞 **Support**

For questions about the experiment design or implementation:
- Check `PROJECT_SUMMARY.md` for technical details
- Review test files in `tests/` for usage examples
- All components are documented and tested

---

**Version**: 2.0 (December 2024)  
**Status**: ✅ **Fully Functional**  
**Compatibility**: PsychoPy 2025.1.1, Python 3.8+, PyQt6 