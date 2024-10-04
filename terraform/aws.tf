resource "aws_s3_bucket" "images" {
  bucket_prefix = "meme-images"
  force_destroy = var.destroy_data
  tags          = var.tags
}

resource "aws_s3_bucket_ownership_controls" "images" {
  bucket = aws_s3_bucket.images.id
  rule {
    object_ownership = "BucketOwnerPreferred"
  }
}

resource "aws_s3_bucket_public_access_block" "images" {
  bucket                  = aws_s3_bucket.images.id
  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

resource "aws_s3_bucket_policy" "public_access_images" {
  bucket = aws_s3_bucket.images.id
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect    = "Allow",
        Principal = "*",
        Action    = "s3:GetObject",
        Resource  = "arn:aws:s3:::${aws_s3_bucket.images.id}/*"
      },
     ]
  })
  depends_on = [
    aws_s3_bucket_public_access_block.images,
    aws_s3_bucket_ownership_controls.images
  ]
}

resource "aws_s3_bucket" "backups" {
  bucket_prefix = "meme-backups"
  force_destroy = var.destroy_data
  tags          = var.tags
}

resource "aws_s3_bucket_lifecycle_configuration" "expire_backups" {
  bucket = aws_s3_bucket.backups.id
  rule {
    id     = "delete_old_backups"
    status = "Enabled"
    expiration { days = 90 }
    filter { prefix = "" }
  }
}

resource "aws_iam_user" "meme" {
  name = "meme"
  tags = var.tags
}

resource "aws_iam_access_key" "meme" {
  user    = aws_iam_user.meme.name
}

resource "aws_iam_policy" "write_s3_buckets" {
  name        = "S3WritePolicy"
  description = "Write access to images S3 bucket"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action   = [
          "s3:PutObject",
          "s3:PutObjectAcl",
          "s3:DeleteObject"
        ]
        Effect   = "Allow"
        Resource = [
            "arn:aws:s3:::${aws_s3_bucket.images.id}/*",
            "arn:aws:s3:::${aws_s3_bucket.backups.id}/*"
        ]
      }
    ]
  })
}

resource "aws_iam_user_policy_attachment" "meme_user_write_s3_buckets" {
  user       = aws_iam_user.meme.name
  policy_arn = aws_iam_policy.write_s3_buckets.arn
}

resource "aws_iam_policy" "ses_send_email_policy" {
  name        = "SESSendEmailPolicy"
  description = "Allows sending emails using AWS SES"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = [
          "ses:SendEmail",
          "ses:SendRawEmail"
        ]
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_user_policy_attachment" "attach_ses_policy_to_user" {
  user       = aws_iam_user.meme.name
  policy_arn = aws_iam_policy.ses_send_email_policy.arn
}