
Virtual Gesture Keyboard ✨⌨️<br><br>

A futuristic AI-powered virtual keyboard controlled entirely using hand gestures in real time.<br>
Built with Computer Vision using OpenCV and MediaPipe, this project allows users to type without touching a physical keyboard.<br>
<br>
The system tracks hand landmarks through a webcam, detects finger gestures, and converts them into keyboard inputs with smooth UI animations and modern glassmorphism effects.
<br><br>
🚀 Features<br>
🖐 Real-time hand tracking using MediaPipe<br>
⌨️ Virtual keyboard controlled by finger gestures<br>
👆 Hover detection with animated buttons<br>
🤏 Pinch gesture for key press detection<br>
🌟 Modern glassmorphism UI<br>
🔤 Dynamic keyboard layout<br>
🔄 Toggle keyboard visibility<br>
🧠 Smooth animations and transitions<br>
📷 Fullscreen webcam interface<br>
💻 Simulates actual keyboard input using PyAutoGUI<br><br>
🛠 Technologies Used<br>
Python,
OpenCV,
MediaPipe,
PyAutoGUI,
NumPy<br>
📌 How It Works
Webcam captures live video feed.<br>
MediaPipe detects hand landmarks.<br>
Index finger acts as the cursor.<br>
Distance between index and middle finger is calculated.<br>
When fingers come close together, a key press is triggered.<br>
PyAutoGUI sends real keyboard inputs to the system.<br><br>
🎯 Hand Controls<br>
Gesture	Action<br>
Move Index Finger	Move cursor over keys<br>
Pinch Index + Middle Finger	Press key<br>
Hover on Button	Highlight key<br>
Toggle Button	Show/Hide keyboard<br><br>


   

Dynamic UI Rendering
📸 Future Improvements
🎙 Voice typing integration
🌐 Multi-language support
😊 Emoji keyboard
🤖 AI predictive text
📱 Mobile version
🖱 Air mouse functionality
🧾 Gesture shortcuts
💡 Applications
Touchless Interfaces
Smart Classrooms
Accessibility Systems
AR/VR Interaction
Public Kiosks
Healthcare Environments
Future Human-Computer Interaction Systems
👨‍💻 Author

Developed by Rahul Dev Bera

⭐ Support

If you like this project:

Star the repository
Fork the project
Contribute improvements
Share with others
📜 License

This project is open-source and available under the MIT License.
