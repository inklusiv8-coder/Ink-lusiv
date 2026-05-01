#!/usr/bin/env python3
# Update HTML modal to modern chat design

# Read the HTML file
with open(r'c:\Users\USER\OneDrive\Documents\ayomide web dev\ink-lusiv work\index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find and replace the AI Chat Modal section
old_modal = '''    <!-- AI Chat Modal -->
    <div id="whatsappChatModal" class="modal">
        <div class="modal-content auth-modal whatsapp-modal">
            <span class="close">&times;</span>
            <div class="chat-header">
                <i class="fas fa-robot"></i>
                <h2 id="chatModalTitle">AI Assistant</h2>
            </div>
            <p class="whatsapp-description">Send us an AI message here and we will respond shortly.</p>
            <form id="whatsappChatForm">
                <div class="form-group">
                    <label for="whatsappName">Your Name</label>
                    <input type="text" id="whatsappName" placeholder="Enter your name" required>
                </div>
                <div class="form-group">
                    <label for="whatsappMessage">AI Message</label>
                    <textarea id="whatsappMessage" placeholder="Type your AI message" rows="4" required></textarea>
                </div>
                <button type="submit" class="btn btn-primary whatsapp-submit-btn">Send</button>
            </form>
            <p class="whatsapp-footer-text">We will receive your AI message and get back to you soon.</p>
        </div>
    </div>'''

new_modal = '''    <!-- AI Chat Modal -->
    <div id="whatsappChatModal" class="modal">
        <div class="modal-content chat-modal-modern">
            <!-- Chat Header -->
            <div class="chat-header-modern">
                <div class="chat-header-left">
                    <span class="close">&times;</span>
                    <div class="chat-brand">
                        <i class="fas fa-robot"></i>
                        <div class="brand-info">
                            <h3 id="chatModalTitle">AI Assistant</h3>
                            <p class="reply-time">Typically replies within 1 hour</p>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Chat Messages Display -->
            <div class="chat-messages" id="chatMessagesContainer">
                <div class="message bot-message">
                    <div class="message-bubble">
                        <p>Hello! 👋</p>
                        <p>How can we help you today?</p>
                    </div>
                    <span class="message-time">Just now</span>
                </div>
            </div>

            <!-- User Info Form (first time only) -->
            <div id="userInfoForm" class="user-info-section">
                <div class="form-group">
                    <label for="whatsappName">Your Name</label>
                    <input type="text" id="whatsappName" placeholder="Enter your name" required>
                </div>
            </div>

            <!-- Message Input Area -->
            <div class="chat-input-area">
                <form id="whatsappChatForm" class="message-input-form">
                    <input type="hidden" id="whatsappMessage" />
                    <div class="input-group">
                        <textarea id="messageInput" placeholder="Type a message..." rows="1" required></textarea>
                        <button type="submit" class="send-btn" title="Send">
                            <i class="fas fa-paper-plane"></i>
                        </button>
                    </div>
                </form>
            </div>
        </div>
    </div>'''

if old_modal in content:
    content = content.replace(old_modal, new_modal)
    with open(r'c:\Users\USER\OneDrive\Documents\ayomide web dev\ink-lusiv work\index.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print("HTML modal updated successfully")
else:
    print("Modal not found - checking for variations...")
    print(f"Old modal length: {len(old_modal)}")
