"""
Email notifications using Gmail SMTP
Sends price alert emails when prices drop below threshold
"""

import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from config import GMAIL_EMAIL, GMAIL_PASSWORD, EMAIL_RECIPIENT

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmailNotifier:
    """Sends price alert emails via Gmail"""
    
    def __init__(self, sender_email=GMAIL_EMAIL, sender_password=GMAIL_PASSWORD):
        self.sender_email = sender_email
        self.sender_password = sender_password
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
    
    def validate_credentials(self):
        """Test if email credentials are valid"""
        if not self.sender_email or not self.sender_password:
            logger.error("❌ Email credentials not configured")
            return False
        
        try:
            # Try to connect and login
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.sender_email, self.sender_password)
            server.quit()
            logger.info("✅ Email credentials validated")
            return True
        except smtplib.SMTPAuthenticationError:
            logger.error("❌ Email authentication failed - check username/password")
            return False
        except Exception as e:
            logger.error(f"❌ Email connection error: {e}")
            return False
    
    def send_email(self, recipient_email, subject, html_body, text_body=None):
        """
        Send an email
        
        Args:
            recipient_email: Email address to send to
            subject: Email subject line
            html_body: HTML formatted email body
            text_body: Plain text fallback
        
        Returns:
            bool: True if sent successfully
        """
        
        if not text_body:
            # Create plain text version from HTML
            text_body = html_body.replace("<br>", "\n").replace("<p>", "").replace("</p>", "")
        
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = self.sender_email
            message["To"] = recipient_email
            
            # Attach both text and HTML versions
            part1 = MIMEText(text_body, "plain")
            part2 = MIMEText(html_body, "html")
            
            message.attach(part1)
            message.attach(part2)
            
            # Send email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.sender_email, self.sender_password)
            server.sendmail(self.sender_email, recipient_email, message.as_string())
            server.quit()
            
            logger.info(f"✅ Email sent to {recipient_email}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to send email: {e}")
            return False
    
    def send_price_alert(self, departure, arrival, price, average_price, date, threshold=None, url=None):
        """
        Send a price alert email
        
        Args:
            departure: Departure airport code
            arrival: Arrival airport code
            price: Current price found
            average_price: Average price from history
            date: Flight date
            threshold: Price threshold that was crossed (e.g., 40, 35, 30)
            url: Link to Ryanair booking page
        """
        
        threshold_text = f" - Below €{threshold}" if threshold else ""
        subject = f"🎉 Price Alert: {departure} → {arrival} at €{price:.2f}{threshold_text}"
        
        # Calculate price difference
        savings = ((average_price - price) / average_price * 100) if average_price else 0
        
        # Create HTML email body
        html_body = f"""
        <html>
            <body style="font-family: Arial, sans-serif; color: #333;">
                <h2 style="color: #2ecc71;">✈️ Price Alert: Price Crossed Threshold!</h2>
                
                <div style="background-color: #f0f0f0; padding: 20px; border-radius: 5px; margin: 20px 0;">
                    <h3>Flight Details:</h3>
                    <p><strong>Route:</strong> {departure} → {arrival}</p>
                    <p><strong>Date:</strong> {date}</p>
                    <p><strong>Current Price:</strong> <span style="font-size: 24px; color: #2ecc71;">€{price:.2f}</span></p>
                    {f'<p><strong>Threshold Hit:</strong> <span style="color: #e67e22;">Below €{threshold}</span></p>' if threshold else ''}
                    <p><strong>Average Price:</strong> €{average_price:.2f}</p>
                    {f'<p><strong>Savings:</strong> <span style="color: #e74c3c;">-€{average_price - price:.2f} ({savings:.1f}%)</span></p>' if savings > 0 else ''}
                </div>
                
                <div style="margin: 20px 0;">
                    <h3>Next Steps:</h3>
                    <ol>
                        <li>Visit <a href="https://www.ryanair.com">Ryanair.com</a></li>
                        <li>Search for flights from <strong>{departure}</strong> to <strong>{arrival}</strong></li>
                        <li>Book your flight before prices increase!</li>
                    </ol>
                </div>
                
                <div style="background-color: #ecf0f1; padding: 15px; border-left: 4px solid #3498db; margin: 20px 0;">
                    <p style="margin: 0; color: #555;">
                        <strong>💡 Tip:</strong> Prices can change quickly. 
                        Check the website immediately to confirm this price is still available.
                    </p>
                </div>
                
                <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
                
                <p style="color: #999; font-size: 12px;">
                    Sent by Ryanair Price Tracker Bot<br>
                    Checked at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                </p>
            </body>
        </html>
        """
        
        text_body = f"""
✈️ PRICE ALERT: Price Crossed Threshold!

Flight Details:
Route: {departure} → {arrival}
Date: {date}
Current Price: €{price:.2f}
{f'Threshold Hit: Below €{threshold}' if threshold else ''}
Average Price: €{average_price:.2f}

Savings: €{average_price - price:.2f} ({savings:.1f}%)

Next Steps:
1. Visit Ryanair.com
2. Search {departure} to {arrival}
3. Book immediately!

Sent by Ryanair Price Tracker Bot
Checked at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        return self.send_email(EMAIL_RECIPIENT, subject, html_body, text_body)
    
    def send_price_report(self, departure, arrival, price, average_price, date):
        """
        Send a regular price report email (sent with every check)
        
        Args:
            departure: Departure airport code
            arrival: Arrival airport code
            price: Current lowest price found
            average_price: Average price from history
            date: Flight date
        """
        
        subject = f"📊 Price Update: {departure} → {arrival} at €{price:.2f}"
        
        # Calculate difference from average
        change = price - average_price
        change_percent = (change / average_price * 100) if average_price else 0
        trend = "📉 Lower" if change < 0 else "📈 Higher" if change > 0 else "→ Same"
        
        html_body = f"""
        <html>
            <body style="font-family: Arial, sans-serif; color: #333;">
                <h2 style="color: #3498db;">📊 Price Update Report</h2>
                
                <div style="background-color: #ecf0f1; padding: 20px; border-radius: 5px; margin: 20px 0;">
                    <h3>Current Prices:</h3>
                    <p><strong>Route:</strong> {departure} → {arrival}</p>
                    <p><strong>Date:</strong> {date}</p>
                    <p><strong>Lowest Price Found:</strong> <span style="font-size: 28px; color: #2ecc71; font-weight: bold;">€{price:.2f}</span></p>
                    <p><strong>Average Price:</strong> €{average_price:.2f}</p>
                    <p><strong>Price Trend:</strong> {trend} {change:+.2f}€ ({change_percent:+.1f}%)</p>
                </div>
                
                <div style="background-color: #fff3cd; padding: 15px; border-left: 4px solid #ffc107; margin: 20px 0;">
                    <p style="margin: 0;"><strong>💡 Action:</strong> Check Ryanair.com to compare current prices and book if interested.</p>
                </div>
                
                <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
                
                <p style="color: #999; font-size: 12px;">
                    Sent by Ryanair Price Tracker Bot<br>
                    Regular price update check at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                </p>
            </body>
        </html>
        """
        
        text_body = f"""
📊 PRICE UPDATE REPORT

Route: {departure} → {arrival}
Date: {date}

Current Price: €{price:.2f}
Average Price: €{average_price:.2f}
Trend: {trend} {change:+.2f}€ ({change_percent:+.1f}%)

Check Ryanair.com for more details and to book if interested.

Sent by Ryanair Price Tracker Bot
Checked at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        return self.send_email(EMAIL_RECIPIENT, subject, html_body, text_body)


# Test function
if __name__ == "__main__":
    notifier = EmailNotifier()
    
    logger.info("Testing email notifier...")
    logger.info(f"Sender email: {notifier.sender_email}")
    logger.info(f"Recipient email: {EMAIL_RECIPIENT}")
    
    # Validate credentials
    if notifier.validate_credentials():
        logger.info("✅ Email credentials are valid!")
        
        # Send test email
        test_result = notifier.send_price_alert(
            departure="TLL",
            arrival="NUE",
            price=42.50,
            average_price=55.00,
            date="2026-05-10"
        )
        
        if test_result:
            logger.info("✅ Test email sent successfully!")
        else:
            logger.error("❌ Failed to send test email")
    else:
        logger.error("❌ Email credentials are invalid or not configured")
        logger.info("\n📝 Please configure:")
        logger.info("   1. Set GMAIL_EMAIL in .env")
        logger.info("   2. Set GMAIL_PASSWORD in .env (use app password, not main password)")
        logger.info("   See setup instructions for details")
