variable "hcloud_token" {
    type = string
}

variable "aws" {
    type = object({
      region            = string
      aws_access_key_id = string
      secret_access_key = string
    })
}

variable "ssh_public_key" {
    type        = string
    description = "Your SSH public key"
}

variable "session_encoder_key" {
    type        = string
    default     = "QXEs3ZChrduSxkHT48WweK"
    description = "Random strong password"
}

variable "location" {
    type    = string
    default = "nbg1"
}

variable "instance_type" {
    type        = string
    default     = "cx22"
    description = "Hetzner VM size"
}

variable "primary_ip" {
    type        = object({
      meme = bool
      wiki = bool
    })
    default = {
      meme = false
      wiki = false
    }
    description = "You can set up primary IPs if you want to keep the IPs even after destroying the env. The IP is charged regardless but you don't have update your DNS record"
}

variable "domain" {
    type = string
    default = "bme.lol"
}

variable "postgres" {
    type = object({
        username = string
        password = string
    })
    default = {
        username = "tatli"
        password = "tatli"
    }
    description = "This user is automatically created and it owns the MEME DataBase"
}

variable "sender_email" {
    type    = string
    default = "bme.lol@protonmail.com"
}

variable "tags" {
    type    = map(string)
    default = {
        Managed_By = "Terrafom"
    }
}

variable "destroy_data" {
    type = bool
    default = false
    description = "Setting this to true deletes all data on terraform destroy. Do not set to true on production."
}

variable "debug" {
    type    = bool
    default = false
}