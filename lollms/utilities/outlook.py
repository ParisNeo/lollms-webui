import win32com.client
from win32com.client import Dispatch

class OutlookUtilities:
    def __init__(self):
        try:
            self.outlook = Dispatch("Outlook.Application").GetNamespace("MAPI")
        except Exception as e:
            print(f"Failed to initialize Outlook: {e}")
            self.outlook = None

    def open_outlook(self):
        # This function doesn't need to do anything in code
        # Opening Outlook is handled by the Dispatch call in __init__
        pass

    def get_email_addresses(self):
        """Returns a list of email addresses from the user's inbox."""
        if not self.outlook:
            print("Outlook is not initialized.")
            return []
        try:
            inbox = self.outlook.GetDefaultFolder(6)  # 6 refers to the inbox
            emails = inbox.Items
            email_addresses = set()
            for email in emails:
                email_addresses.add(email.SenderEmailAddress)
            return list(email_addresses)
        except Exception as e:
            print(f"Failed to get email addresses: {e}")
            return []

    def load_mails_from_address(self, address):
        """Loads all mails received from a specific email address.

        Args:
            address (str): The email address to filter mails from.

        Returns:
            list: A list of email objects received from the specified address.
        """
        if not self.outlook:
            print("Outlook is not initialized.")
            return []
        try:
            inbox = self.outlook.GetDefaultFolder(6)
            emails = inbox.Items
            filtered_emails = []
            for email in emails:
                if email.SenderEmailAddress == address:
                    filtered_emails.append(email)
            return filtered_emails
        except Exception as e:
            print(f"Failed to load mails from {address}: {e}")
            return []

    def send_reply(self, original_mail, reply_message):
        """Sends a reply to an email.

        Args:
            original_mail: The original email object to reply to.
            reply_message (str): The message content for the reply.
        """
        if not self.outlook:
            print("Outlook is not initialized.")
            return
        try:
            reply = original_mail.ReplyAll()
            reply.Body = reply_message
            reply.Send()
        except Exception as e:
            print(f"Failed to send reply: {e}")

# Example usage:
if __name__ == "__main__":
    outlook_utils = OutlookUtilities()
    outlook_utils.open_outlook()  # Not necessary to call, but here for clarity
    email_addresses = outlook_utils.get_email_addresses()
    print("Email addresses found:", email_addresses)

    specific_address = 'example@example.com'
    emails_from_address = outlook_utils.load_mails_from_address(specific_address)
    print(f"Loaded {len(emails_from_address)} emails from {specific_address}")

    if emails_from_address:
        outlook_utils.send_reply(emails_from_address[0], "This is a test reply.")
        print("Reply sent.")
