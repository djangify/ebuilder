"""
Management command to create default policy pages for eBuilder.
These pages are created on first boot to prevent 404 errors
and provide templates for store owners to customise.
"""

from django.core.management.base import BaseCommand
from infopages.models import InfoPage


class Command(BaseCommand):
    help = "Creates default policy pages (cookie, privacy, terms, refund)"

    def handle(self, *args, **options):
        policies = [
            {
                "title": "Cookie Policy",
                "slug": "cookie-policy",
                "content": self.get_cookie_policy_content(),
            },
            {
                "title": "Privacy Policy",
                "slug": "privacy-policy",
                "content": self.get_privacy_policy_content(),
            },
            {
                "title": "Terms and Conditions",
                "slug": "terms-and-conditions",
                "content": self.get_terms_content(),
            },
            {
                "title": "Refund Policy",
                "slug": "refund-policy",
                "content": self.get_refund_policy_content(),
            },
        ]

        created_count = 0
        for policy in policies:
            obj, created = InfoPage.objects.get_or_create(
                slug=policy["slug"],
                defaults={
                    "title": policy["title"],
                    "content": policy["content"],
                    "page_type": "policy",
                    "published": True,
                },
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"Created: {policy['title']}"))
            else:
                self.stdout.write(
                    self.style.WARNING(f"Already exists: {policy['title']}")
                )

        self.stdout.write(
            self.style.SUCCESS(f"\nDefault policies complete: {created_count} created")
        )

    def get_update_notice(self):
        """Standard notice that appears at the top of all default pages."""
        return """
<div style="background-color: #fef3c7; border: 2px solid #f59e0b; border-radius: 8px; padding: 20px; margin-bottom: 30px;">
    <p style="margin: 0; color: #92400e; font-weight: 600;">
        ⚠️ <strong>ACTION REQUIRED:</strong> This is a template page. Please update this content with your specific business details, contact information, and policies before launching your store. Delete this notice once you have customised the page.
    </p>
</div>
"""

    def get_cookie_policy_content(self):
        return f"""
{self.get_update_notice()}

<h2>What Are Cookies</h2>
<p>Cookies are small text files that are placed on your computer or mobile device when you visit our website. They are widely used to make websites work more efficiently and provide information to the website owners.</p>

<h2>How We Use Cookies</h2>
<p>We use cookies for the following purposes:</p>

<h3>Essential Cookies</h3>
<p>These cookies are necessary for the website to function properly. They enable core functionality such as:</p>
<ul>
    <li>Shopping cart functionality</li>
    <li>User authentication and session management</li>
    <li>Security features (CSRF protection)</li>
</ul>
<p>Without these cookies, the website cannot function properly.</p>

<h3>Preference Cookies</h3>
<p>These cookies remember choices you make to improve your experience, such as:</p>
<ul>
    <li>Cookie consent preferences</li>
    <li>Display preferences</li>
</ul>

<h3>Analytics Cookies</h3>
<p>[If you use analytics, describe them here. If not, remove this section.]</p>

<h2>Third-Party Cookies</h2>
<p>We use Stripe for payment processing. Stripe may set cookies to help detect fraud and process payments securely. Please refer to <a href="https://stripe.com/privacy" target="_blank" rel="noopener">Stripe's Privacy Policy</a> for more information.</p>

<h2>Managing Cookies</h2>
<p>Most web browsers allow you to control cookies through their settings. You can usually find these settings in the "Options" or "Preferences" menu of your browser. However, please note that disabling essential cookies may prevent you from using certain features of our website, including making purchases.</p>

<h2>Contact Us</h2>
<p>If you have questions about our use of cookies, please contact us at: <strong>[YOUR EMAIL ADDRESS]</strong></p>

<p><em>Last updated: [DATE]</em></p>
"""

    def get_privacy_policy_content(self):
        return f"""
{self.get_update_notice()}

<h2>Introduction</h2>
<p><strong>[YOUR BUSINESS NAME]</strong> ("we", "our", or "us") is committed to protecting your privacy. This Privacy Policy explains how we collect, use, and safeguard your information when you visit our website and make purchases.</p>

<h2>Information We Collect</h2>

<h3>Information You Provide</h3>
<p>When you create an account or make a purchase, we collect:</p>
<ul>
    <li>Name and email address</li>
    <li>Account password (stored securely using encryption)</li>
    <li>Order history and download records</li>
</ul>

<h3>Payment Information</h3>
<p>Payment processing is handled entirely by Stripe. We do not store your credit card details on our servers. Please refer to <a href="https://stripe.com/privacy" target="_blank" rel="noopener">Stripe's Privacy Policy</a> for information about how they handle your payment data.</p>

<h3>Automatically Collected Information</h3>
<p>When you visit our website, we may automatically collect:</p>
<ul>
    <li>IP address</li>
    <li>Browser type and version</li>
    <li>Pages visited and time spent</li>
    <li>Referring website</li>
</ul>

<h2>How We Use Your Information</h2>
<p>We use your information to:</p>
<ul>
    <li>Process your orders and provide access to purchased downloads</li>
    <li>Send order confirmations and important account notifications</li>
    <li>Respond to your enquiries and provide customer support</li>
    <li>Improve our website and services</li>
    <li>Comply with legal obligations</li>
</ul>

<h2>Data Retention</h2>
<p>We retain your account information and order history for as long as your account is active or as needed to provide you access to your purchased products. You may request deletion of your account by contacting us.</p>

<h2>Your Rights</h2>
<p>Depending on your location, you may have the right to:</p>
<ul>
    <li>Access the personal data we hold about you</li>
    <li>Request correction of inaccurate data</li>
    <li>Request deletion of your data</li>
    <li>Object to or restrict processing of your data</li>
    <li>Data portability</li>
</ul>

<h2>Data Security</h2>
<p>We implement appropriate technical and organisational measures to protect your personal data against unauthorised access, alteration, disclosure, or destruction.</p>

<h2>Third-Party Services</h2>
<p>We use the following third-party services:</p>
<ul>
    <li><strong>Stripe</strong> - Payment processing</li>
    <li><strong>[List any analytics, email services, etc.]</strong></li>
</ul>

<h2>Changes to This Policy</h2>
<p>We may update this Privacy Policy from time to time. We will notify you of any significant changes by posting a notice on our website.</p>

<h2>Contact Us</h2>
<p>For privacy-related enquiries, please contact us at:</p>
<p>
    <strong>[YOUR BUSINESS NAME]</strong><br>
    Email: <strong>[YOUR EMAIL ADDRESS]</strong><br>
    [YOUR ADDRESS - if applicable]
</p>

<p><em>Last updated: [DATE]</em></p>
"""

    def get_terms_content(self):
        return f"""
{self.get_update_notice()}

<h2>1. Introduction</h2>
<p>These Terms and Conditions ("Terms") govern your use of <strong>[YOUR WEBSITE URL]</strong> ("the Website") and any purchases you make. By using our Website and purchasing products, you agree to these Terms.</p>

<p><strong>[YOUR BUSINESS NAME]</strong> operates this Website. References to "we", "our", or "us" refer to the business operator.</p>

<h2>2. Products and Services</h2>
<p>We sell digital download products. Upon successful payment, you will receive access to download your purchased files. All products are delivered electronically - no physical items will be shipped.</p>

<h2>3. Account Registration</h2>
<p>To make a purchase, you must create an account with a valid email address. You are responsible for:</p>
<ul>
    <li>Maintaining the confidentiality of your account credentials</li>
    <li>All activities that occur under your account</li>
    <li>Notifying us immediately of any unauthorised access</li>
</ul>

<h2>4. Pricing and Payment</h2>
<p>All prices are displayed in <strong>[YOUR CURRENCY]</strong> and include applicable taxes unless otherwise stated. Payment is processed securely through Stripe. We accept major credit and debit cards.</p>

<h2>5. Digital Product Licence</h2>
<p>When you purchase a digital product, you receive a licence to use that product subject to the following conditions:</p>
<ul>
    <li>The licence is for personal/commercial use [SPECIFY WHICH]</li>
    <li>You may not redistribute, resell, or share the files</li>
    <li>You may not claim the products as your own creation</li>
    <li>[ADD ANY SPECIFIC LICENCE TERMS FOR YOUR PRODUCTS]</li>
</ul>

<h2>6. Download Limits</h2>
<p>Each purchase includes a limited number of downloads as specified on the product page. Once you have reached the download limit, you will need to contact us for additional access.</p>

<h2>7. Refunds</h2>
<p>Please refer to our <a href="/policies/refund-policy/">Refund Policy</a> for information about refunds and cancellations.</p>

<h2>8. Intellectual Property</h2>
<p>All content on this Website, including but not limited to text, graphics, logos, images, and digital products, is the property of <strong>[YOUR BUSINESS NAME]</strong> or our content suppliers and is protected by intellectual property laws.</p>

<h2>9. Limitation of Liability</h2>
<p>To the maximum extent permitted by law, we shall not be liable for any indirect, incidental, special, consequential, or punitive damages arising from your use of our Website or products.</p>

<h2>10. Governing Law</h2>
<p>These Terms are governed by the laws of <strong>[YOUR COUNTRY/JURISDICTION]</strong>. Any disputes shall be subject to the exclusive jurisdiction of the courts of <strong>[YOUR JURISDICTION]</strong>.</p>

<h2>11. Changes to Terms</h2>
<p>We reserve the right to modify these Terms at any time. Continued use of the Website after changes constitutes acceptance of the new Terms.</p>

<h2>12. Contact</h2>
<p>For questions about these Terms, please contact us at: <strong>[YOUR EMAIL ADDRESS]</strong></p>

<p><em>Last updated: [DATE]</em></p>
"""

    def get_refund_policy_content(self):
        return f"""
{self.get_update_notice()}

<h2>Digital Products - Important Information</h2>
<p>Please read this policy carefully before making a purchase. Due to the nature of digital products, our refund policy differs from physical goods.</p>

<h2>Our Refund Policy</h2>
<p>Because digital products can be downloaded and copied instantly, <strong>we generally do not offer refunds</strong> once a product has been downloaded.</p>

<h2>When We May Offer Refunds</h2>
<p>We will consider refunds in the following circumstances:</p>
<ul>
    <li><strong>Technical Issues:</strong> If you are unable to download or access your purchased files due to technical problems on our end, and we cannot resolve the issue</li>
    <li><strong>Duplicate Purchase:</strong> If you accidentally purchased the same product twice</li>
    <li><strong>Product Not As Described:</strong> If the product is significantly different from its description</li>
    <li><strong>Corrupted Files:</strong> If the files are corrupted and we cannot provide working replacements</li>
</ul>

<h2>Refund Request Process</h2>
<p>To request a refund:</p>
<ol>
    <li>Contact us at <strong>[YOUR EMAIL ADDRESS]</strong> within <strong>[NUMBER]</strong> days of purchase</li>
    <li>Include your order number and the reason for your request</li>
    <li>We will review your request and respond within <strong>[NUMBER]</strong> business days</li>
</ol>

<h2>Non-Refundable Situations</h2>
<p>We cannot offer refunds if:</p>
<ul>
    <li>You have already downloaded the files</li>
    <li>You changed your mind after purchase</li>
    <li>The product doesn't meet expectations that weren't part of the product description</li>
    <li>You don't have the required software to use the product (system requirements are listed on product pages)</li>
</ul>

<h2>Before You Buy</h2>
<p>We encourage you to:</p>
<ul>
    <li>Read the full product description carefully</li>
    <li>Check any system requirements or compatibility information</li>
    <li>Review any preview images or samples provided</li>
    <li>Contact us with questions before purchasing</li>
</ul>

<h2>Contact Us</h2>
<p>If you have any questions about this policy or need assistance with a purchase, please contact us at: <strong>[YOUR EMAIL ADDRESS]</strong></p>

<p><em>Last updated: [DATE]</em></p>
"""
