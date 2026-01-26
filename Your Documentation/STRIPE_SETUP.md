# Stripe Setup Guide

Complete guide to configuring Stripe payments for your eBuilder store.

---

## Overview

eBuilder uses Stripe for:
- Processing card payments
- Handling checkout sessions
- Managing refunds
- Webhook notifications for order completion

---

## Step 1: Create Stripe Account

1. Go to [stripe.com](https://stripe.com)
2. Click "Start now" and create account
3. Complete business verification (required for live payments)

---

## Step 2: Get API Keys

1. Log into [Stripe Dashboard](https://dashboard.stripe.com)
2. Click **Developers** in the left sidebar
3. Click **API keys**

You'll see:
- **Publishable key** (`pk_test_...` or `pk_live_...`)
- **Secret key** (`sk_test_...` or `sk_live_...`)

**For testing:** Use keys starting with `pk_test_` and `sk_test_`
**For production:** Use keys starting with `pk_live_` and `sk_live_`

Add to your `.env`:
```bash
STRIPE_PUBLIC_KEY=pk_live_your_publishable_key
STRIPE_SECRET_KEY=sk_live_your_secret_key
```

---

## Step 3: Set Up Webhook

Webhooks let Stripe notify your store when payments complete.

### Create Webhook Endpoint

1. In Stripe Dashboard → **Developers** → **Webhooks**
2. Click **Add endpoint**
3. Enter your webhook URL:
   ```
   https://yourdomain.com/shop/stripe/webhook/
   ```
4. Select events to listen for:
   - `checkout.session.completed` (required)
   - `payment_intent.succeeded` (optional)
   - `payment_intent.payment_failed` (optional)
5. Click **Add endpoint**

### Get Webhook Secret

1. Click on your new webhook endpoint
2. Click **Reveal** under "Signing secret"
3. Copy the `whsec_...` value

Add to your `.env`:
```bash
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_signing_secret
```

---

## Step 4: Configure Products in eBuilder

eBuilder handles products dynamically - you don't need to create products in Stripe.

1. Go to your eBuilder admin: `/admin`
2. Navigate to **Shop → Products**
3. Create products with:
   - Title and description
   - Price (in your default currency)
   - Product image
   - Downloadable file(s)
   - Publish status

When customers checkout, eBuilder creates a Stripe Checkout Session with the correct amount.

---

## Step 5: Test Your Setup

### Test Mode (Recommended First)

1. Use test API keys (`pk_test_`, `sk_test_`)
2. Use test card number: `4242 4242 4242 4242`
3. Any future expiry date
4. Any 3-digit CVC

### Test the Full Flow

1. Add a product to cart on your store
2. Proceed to checkout
3. Use test card details
4. Verify order appears in admin
5. Verify webhook received (check Stripe Dashboard → Webhooks → Logs)

---

## Step 6: Go Live

1. Complete Stripe account verification
2. Switch to live API keys in `.env`
3. Update webhook to use live signing secret
4. Restart: `docker compose restart`

---

## Currency Configuration

Set your default currency in eBuilder admin:

1. Go to **Pages → Site Settings**
2. Set **Default Currency** (GBP, USD, EUR, etc.)

Stripe supports 135+ currencies. The currency code must match Stripe's format.

---

## Webhook Events Explained

| Event | What It Means | eBuilder Action |
|-------|---------------|-----------------|
| `checkout.session.completed` | Customer paid successfully | Creates order, grants download access |
| `payment_intent.succeeded` | Payment confirmed | Backup confirmation |
| `payment_intent.payment_failed` | Payment failed | Logs failure |

---

## Troubleshooting

### Webhook not receiving events

1. Check URL is correct: `https://yourdomain.com/shop/stripe/webhook/`
2. URL must be HTTPS (not HTTP)
3. Check for SSL certificate issues
4. Review webhook logs in Stripe Dashboard

### "No such checkout session"

- Webhook secret doesn't match
- Check `STRIPE_WEBHOOK_SECRET` in `.env`
- Make sure it's the webhook secret, not the API secret

### Orders not completing

1. Check webhook is receiving events (Stripe Dashboard → Webhooks → Logs)
2. Check eBuilder logs: `docker compose logs -f`
3. Verify database is writable

### Test payments work, live payments don't

1. Ensure you're using live keys (not test)
2. Check Stripe account is fully verified
3. Some countries require additional verification

### Customer sees error after payment

Usually a webhook configuration issue:
1. Payment succeeded (money collected)
2. But webhook failed to update order
3. Customer should contact you
4. Check order manually in Stripe Dashboard

---

## Refunds

Process refunds through Stripe Dashboard:

1. Go to Stripe Dashboard → **Payments**
2. Find the payment
3. Click **Refund**
4. Choose full or partial refund

eBuilder will receive webhook notification and update order status automatically.

---

## Security Best Practices

1. **Never share secret keys** - The `sk_live_` key can access your money
2. **Use environment variables** - Don't hardcode keys in code
3. **Restrict API key permissions** - In Stripe Dashboard, create restricted keys if needed
4. **Monitor for suspicious activity** - Set up Stripe Radar alerts
5. **Keep webhook secret private** - It validates webhook authenticity

---

## Stripe Fees

Check Stripe for current rates.

No monthly fees. You only pay when you receive payments.

---

## Support

- **Stripe Documentation:** [stripe.com/docs](https://stripe.com/docs)
- **Stripe Support:** [support.stripe.com](https://support.stripe.com)
- **eBuilder Issues:** Check your product documentation