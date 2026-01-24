# shop/management/commands/test_email.py
"""
Management command to test email configuration.
Usage: python manage.py test_email --to your@email.com
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from django.core.management.base import BaseCommand

from shop.config_manager import ConfigManager


class Command(BaseCommand):
    help = "Test email SMTP connection and optionally send a test email"

    def add_arguments(self, parser):
        parser.add_argument(
            "--to",
            type=str,
            help="Email address to send test message to",
        )
        parser.add_argument(
            "--connection-only",
            action="store_true",
            help="Only test SMTP connection, do not send email",
        )

    def handle(self, *args, **options):
        self.stdout.write("\nTesting email configuration...\n")

        config = ConfigManager.get_email_config()

        # Check if configured
        if not config["host"]:
            self.stdout.write(
                self.style.ERROR(
                    "✗ Email host not configured\n"
                    "  Set EMAIL_HOST in .env or configure in Admin > Shop Settings"
                )
            )
            return

        self.stdout.write(f"Host: {config['host']}")
        self.stdout.write(f"Port: {config['port']}")
        self.stdout.write(f"TLS: {'Yes' if config['use_tls'] else 'No'}")
        self.stdout.write(f"Username: {config['username'] or 'Not set'}")
        self.stdout.write(f"From: {config['from_address'] or 'Not set'}")

        # Test SMTP connection
        try:
            self.stdout.write("\nConnecting to SMTP server...")

            if config["use_tls"]:
                server = smtplib.SMTP(config["host"], config["port"], timeout=30)
                server.starttls(context=ssl.create_default_context())
            else:
                server = smtplib.SMTP_SSL(config["host"], config["port"], timeout=30)

            self.stdout.write(self.style.SUCCESS("✓ Connected to SMTP server"))

            # Try authentication if credentials provided
            if config["username"] and config["password"]:
                self.stdout.write("Authenticating...")
                server.login(config["username"], config["password"])
                self.stdout.write(self.style.SUCCESS("✓ Authentication successful"))
            else:
                self.stdout.write(
                    self.style.WARNING("⚠ No credentials provided - skipping auth")
                )

            # Send test email if requested
            if options["to"] and not options["connection_only"]:
                self.stdout.write(f"\nSending test email to {options['to']}...")

                msg = MIMEMultipart("alternative")
                msg["Subject"] = "eBuilder Email Test"
                msg["From"] = config["from_address"] or config["username"]
                msg["To"] = options["to"]

                text = """
eBuilder Email Test

If you're reading this, your email configuration is working correctly!

Configured settings:
- Host: {host}
- Port: {port}
- TLS: {tls}
- From: {from_addr}
                """.format(
                    host=config["host"],
                    port=config["port"],
                    tls="Yes" if config["use_tls"] else "No",
                    from_addr=config["from_address"] or config["username"],
                )

                html = f"""
                <html>
                <body style="font-family: sans-serif; padding: 20px;">
                    <h2 style="color: #4CAF50;">✓ eBuilder Email Test</h2>
                    <p>If you're reading this, your email configuration is working correctly!</p>
                    <hr style="border: 1px solid #eee;">
                    <p><strong>Configured settings:</strong></p>
                    <ul>
                        <li>Host: {config["host"]}</li>
                        <li>Port: {config["port"]}</li>
                        <li>TLS: {"Yes" if config["use_tls"] else "No"}</li>
                        <li>From: {config["from_address"] or config["username"]}</li>
                    </ul>
                </body>
                </html>
                """

                msg.attach(MIMEText(text, "plain"))
                msg.attach(MIMEText(html, "html"))

                server.send_message(msg)
                self.stdout.write(
                    self.style.SUCCESS(f"✓ Test email sent to {options['to']}")
                )

            server.quit()
            self.stdout.write(
                self.style.SUCCESS("\n✓ Email configuration test passed!")
            )

        except smtplib.SMTPAuthenticationError as e:
            self.stdout.write(self.style.ERROR(f"\n✗ Authentication failed: {e}"))
            self.stdout.write("  Check your username and password")

        except smtplib.SMTPConnectError as e:
            self.stdout.write(self.style.ERROR(f"\n✗ Connection failed: {e}"))
            self.stdout.write("  Check host, port, and TLS settings")

        except smtplib.SMTPException as e:
            self.stdout.write(self.style.ERROR(f"\n✗ SMTP error: {e}"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"\n✗ Unexpected error: {e}"))

        self.stdout.write("")
