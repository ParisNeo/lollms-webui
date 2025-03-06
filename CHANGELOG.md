# LoLLMs v19.0 (alpha) Changelog
*Date: March 06, 2025*

## Core Settings Enhancements
- **Revamped Main Settings Structure**: The primary settings interface has been reorganized to improve usability and maintainability, providing streamlined access to essential configuration options.

## Application Customization
- **Introduced Application Customization Settings**:  
  - *Custom Application Name*: Users can now define a unique name for the application.  
  - *Custom Application Slogan*: A configurable slogan option has been added for personalized branding.  
  - *Custom Application Logo*: Support for a user-defined logo enhances visual customization.  
  These additions offer extensive flexibility, allowing users to tailor the application’s identity to their specific needs.

## Services System Overhaul
- **Overhauled Services System Architecture**: The services framework has been comprehensively restructured to improve modularity and scalability, facilitating better integration and management of various service types.

## Service Parameter Improvements
- **Enhanced Service Parameter Flexibility**: Service parameters have been redesigned to support dynamic customization, accommodating a broader range of services with configurable options for precise control over functionality.

## Function Call Advancements
- **Expanded Function Call Capabilities**: Function calls now support both static and dynamic parameters. Static parameters ensure consistent predefined values, while dynamic parameters provide adaptability, enhancing control and versatility in execution.

---

# LoLLMs v18.1 Changelog
*Date: Prior to March 06, 2025*

- **System-Wide Function Calling**: Function calling capabilities have been fully implemented across the system for consistent operation.  
- **Full Integration with Lightrag**: Seamless integration with Lightrag has been achieved, enhancing system functionality.  
- **Enhanced User Interface**: The UI has been refined for improved usability and aesthetics.  
- **Reworked Context Management System**: The context management framework has been optimized for better performance and reliability.  
- **Long-Term Memory Reintroduced**: Long-term memory functionality has been restored through a dedicated function call mechanism.  
- **[Video Tutorial](https://youtu.be/0ft6PyOvSqI?si=3bFtOzQ-J2Y53JaY)**: A detailed guide on function calls in LoLLMs is available for user reference.

---

# LoLLMs v18.0 (beta) Changelog
*Date: Prior to v18.1*

- **Discontinued Raw HTML Rendering**: Messages no longer render raw HTML, bolstering security against code injection vulnerabilities. This update aligns with LoLLMs’ compatibility with Docker environments.

---

# LoLLMs v18.0 (alpha) Changelog
## LoLLMs v18 'Matrix'
*Date: Earlier Release*

### Binary Signature
01010100 01001000 01000101 01010010 01000101 00100000 
01001001 01010011 00100000 01001110 01001111 00100000 
01010011 01010000 01001111 01001101 01001110  
(*Translation*: "THERE IS NO SPOON")

## Major Features
- **Implemented "Think First" Process**: A new process requiring AI to deliberate before responding has been integrated into all interactions.  
- **Thinking Visualization UI Component**: A dedicated interface element visualizes the AI’s reasoning process.  
- **Collapsible Thinking Section**: A collapsible section in the chat interface displays the AI’s thought process.  
- **Automatic Changelog Popup Notification System**: A new system notifies users of updates upon version detection.

## User Interface Improvements
- **Collapsible Thinking Process Panel**: Displays the AI’s reasoning steps with an option to collapse for convenience.  
- **Toggle Button**: Enables users to show or hide the thinking process as needed.  
- **Enhanced Step-by-Step Visualization**: Improved formatting enhances readability of the AI’s reasoning stages.  
- **Progress Indicators**: Visual cues indicate progress through the thinking phases.  
- **Changelog Popup Dialog**: Features a modern, scrollable design with a dismissible option and settings menu access.

## AI Enhancements
- **Systematic Thinking Approach**: Structured thinking patterns (hypothesis, analysis, planning) have been integrated for improved reasoning.  
- **Improved Problem-Solving**: Explicit reasoning steps enhance the AI’s problem-solving capabilities.  
- **Enhanced Decision-Making Transparency**: The AI’s decision-making process is now more transparent to users.

## Performance Optimizations
- **Optimized Thinking Process Rendering**: Display of the thinking process has been streamlined for efficiency.  
- **Improved Response Generation Pipeline**: The response generation workflow has been enhanced for better performance.  
- **Better Memory Management**: Memory usage for tracking the thinking process has been optimized.

## Technical Updates
- **New API Endpoints**: Added endpoints for monitoring the thinking process.  
- **Thinking Process Data Structure**: A new data structure supports the thinking framework.  
- **Enhanced Logging System**: Improved logging facilitates thought process tracking.  
- **Changelog Version Tracking System**: Includes local storage for preferences and automated popup triggers.

## Documentation
- **Thinking Process Documentation**: Comprehensive guides for the new thinking features have been added.  
- **Updated User Guide**: Instructions for utilizing the thinking visualization are now included.  
- **Changelog Notification System Documentation**: Details the functionality of the popup system.

## Note
This release demonstrates that advanced thinking capabilities can be achieved with traditional LLMs through effective prompting and visualization, without reliance on specialized models such as O1 or R1.