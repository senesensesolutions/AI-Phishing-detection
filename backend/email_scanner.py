import imaplib
import email
from email.header import decode_header
import os
import sys
import argparse
import time
from dotenv import load_dotenv

# Add the parent directory to sys.path if needed
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from predict import predict_message

# Load environment variables
load_dotenv()

IMAP_SERVER = os.getenv("IMAP_SERVER", "imap.gmail.com")
IMAP_USER = os.getenv("IMAP_USER", "")
IMAP_PASS = os.getenv("IMAP_PASS", "")

def get_text_from_email(msg):
    text_content = ""
    html_content = ""
    
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))
            
            if "attachment" not in content_disposition:
                try:
                    payload = part.get_payload(decode=True)
                    if payload:
                        charset = part.get_content_charset() or 'utf-8'
                        decoded_payload = payload.decode(charset, errors='ignore')
                        
                        if content_type == "text/plain":
                            text_content += decoded_payload + " "
                        elif content_type == "text/html":
                            html_content += decoded_payload + " "
                except Exception as e:
                    print(f"  [Error decoding email part: {e}]")
    else:
        try:
            payload = msg.get_payload(decode=True)
            if payload:
                charset = msg.get_content_charset() or 'utf-8'
                text_content = payload.decode(charset, errors='ignore')
        except Exception as e:
            print(f"  [Error decoding email body: {e}]")
            
    # Prefer plain text, fallback to html if plain text is empty
    return text_content.strip() if text_content.strip() else html_content.strip()

def process_unseen_emails(imap_obj, mark_seen=False):
    # Search for all unseen emails
    status, messages = imap_obj.search(None, 'UNSEEN')
    
    if status != 'OK':
        print("Failed to search for emails.")
        return 0
        
    email_ids = messages[0].split()
    if not email_ids:
        print("No new unread emails.")
        return 0
        
    print(f"Found {len(email_ids)} unseen email(s). Processing...")
    
    for e_id in email_ids:
        # Fetch the email by ID
        # Use (BODY.PEEK[]) if readonly, otherwise (RFC822)
        fetch_cmd = '(BODY.PEEK[])' if not mark_seen else '(RFC822)'
        res, msg_data = imap_obj.fetch(e_id, fetch_cmd)
        
        if res != 'OK':
            print(f"Failed to fetch email ID {e_id}")
            continue
            
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                try:
                    # Parse the raw email bytes
                    msg = email.message_from_bytes(response_part[1])
                    
                    # Decode the subject
                    subject, encoding = decode_header(msg.get("Subject", ""))[0]
                    if isinstance(subject, bytes):
                        encoding = encoding if encoding else 'utf-8'
                        subject = subject.decode(encoding, errors='ignore')
                    
                    print("-" * 50)
                    print(f"📧 Subject: {subject}")
                    
                    # Extract body
                    body = get_text_from_email(msg)
                    
                    # Combine for prediction
                    full_text = f"{subject}\n\n{body}"
                    
                    # Pass through prediction model
                    print("🤖 Analyzing content through AI Phishing Detector...")
                    result = predict_message(full_text)
                    
                    prediction = result.get('prediction', 'unknown')
                    confidence = result.get('confidence', 0.0)
                    
                    if prediction == 'phishing':
                        print(f"⚠️  WARNING: PHISHING DETECTED ⚠️")
                        print(f"🚨 Risk Score: {confidence*100:.1f}%")
                    elif prediction == 'legitimate':
                        print(f"✅ CLEAR: Email appears legitimate.")
                        print(f"🛡️  Confidence: {confidence*100:.1f}%")
                    else:
                        print(f"Result: {prediction} (Confidence: {confidence*100:.1f}%)")
                        
                except Exception as e:
                    print(f"Error processing email ID {e_id.decode()}: {e}")
    
    print("-" * 50)
    return len(email_ids)

def run_loop(imap_obj, delay=60, mark_seen=False):
    print(f"Entering continuous polling mode (every {delay} seconds). Press Ctrl+C to stop.")
    try:
        while True:
            # imap search doesn't get new emails automatically on some servers until NOOP or RECENT
            imap_obj.noop()
            process_unseen_emails(imap_obj, mark_seen)
            time.sleep(delay)
    except KeyboardInterrupt:
        print("\nStopping email scanner loop.")

def main():
    parser = argparse.ArgumentParser(description="Real-Time Email Scanner for Phishing Detection")
    parser.add_argument("--loop", action="store_true", help="Run continuously in a loop")
    parser.add_argument("--delay", type=int, default=60, help="Delay in seconds between checks (if running in loop)")
    parser.add_argument("--mark-seen", action="store_true", help="Mark scanned emails as read (default: readonly peek)")
    args = parser.parse_args()

    if not IMAP_USER or not IMAP_PASS:
        print("Error: Please set IMAP_USER and IMAP_PASS in backend/.env")
        print("Make sure you use an App Password for Gmail/Outlook.")
        sys.exit(1)
        
    print(f"Connecting to IMAP Server: {IMAP_SERVER}...")
    try:
        imap = imaplib.IMAP4_SSL(IMAP_SERVER)
        imap.login(IMAP_USER, IMAP_PASS)
    except Exception as e:
        print(f"Failed to connect or login: {e}")
        sys.exit(1)
        
    # Select inbox (READ-ONLY mode unless --mark-seen is specified)
    readonly = not args.mark_seen
    mode_str = "Read-Only" if readonly else "Read/Write"
    print(f"Selecting INBOX ({mode_str} Mode)...")
    
    try:
        status, messages = imap.select("INBOX", readonly=readonly)
        if status != 'OK':
            print("Failed to select INBOX.")
            return

        if args.loop:
            run_loop(imap, args.delay, args.mark_seen)
        else:
            process_unseen_emails(imap, args.mark_seen)
            
    finally:
        try:
            imap.close()
        except:
            pass
        imap.logout()
        print("Disconnected from IMAP server.")

if __name__ == "__main__":
    main()
