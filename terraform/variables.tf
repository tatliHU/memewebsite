variable "hcloud_token" {
  type = string
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