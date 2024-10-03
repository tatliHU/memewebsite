resource "hcloud_ssh_key" "web" {
  name       = "Webserver key"
  public_key = var.ssh_public_key
}

data "template_file" "cloud_init" {
  template = file("${path.module}/cloud-init.yaml")
  vars = {
    username              = var.postgres.username
    password              = var.postgres.password
    session_encoder_key   = var.session_encoder_key
    aws_image_bucket      = aws_s3_bucket.images.id
    aws_backup_bucket     = aws_s3_bucket.backups.id
    aws_region            = var.aws.region
    aws_access_key_id     = aws_iam_access_key.meme.id
    aws_secret_access_key = aws_iam_access_key.meme.secret
    sender_email          = var.sender_email
    website_url           = "https://${var.domain}"
  }
}

data "hcloud_primary_ip" "meme" {
  count = var.primary_ip.meme ? 1 : 0
  name  = "meme"
}

resource "hcloud_server" "web" {
  image              = "debian-12"
  name               = "meme-webserver"
  server_type        = var.instance_type
  location           = var.location
  user_data = base64encode(data.template_file.cloud_init.rendered)
  public_net {
    ipv4_enabled = true
    ipv4         = var.primary_ip.meme ? data.hcloud_primary_ip.meme[0].id : null
    ipv6_enabled = false
  }
  ssh_keys = [hcloud_ssh_key.web.id]
}

resource "hcloud_firewall" "web" {
  name = "web"
  rule {
    direction = "in"
    protocol  = "icmp"
    source_ips = ["0.0.0.0/0"]
  }
  rule {
    direction = "in"
    protocol  = "tcp"
    port      = "80"
    source_ips = ["0.0.0.0/0"]
  }
  rule {
    direction = "in"
    protocol  = "tcp"
    port      = "22"
    source_ips = ["0.0.0.0/0"]
  }
}

resource "hcloud_firewall_attachment" "web" {
    firewall_id = hcloud_firewall.web.id
    server_ids  = [hcloud_server.web.id]
}