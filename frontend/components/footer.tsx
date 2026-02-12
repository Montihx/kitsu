import React from "react";
import { DiscordLogoIcon, GitHubLogoIcon } from "@radix-ui/react-icons";
import Image from "next/image";
import Container from "./container";
import { Separator } from "./ui/separator";

const Footer = () => {
  return (
    <footer className="w-full bg-card border-t border-border mt-20">
      <Container className="py-12">
        <div className="flex flex-col items-center space-y-6">
          {/* Logo */}
          <div className="flex items-center gap-2">
            <Image 
              src="/icon.png" 
              alt="logo" 
              width="70" 
              height="70" 
              suppressHydrationWarning 
              className="transition-transform duration-300 hover:scale-110"
            />
            <span className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-foreground via-primary to-primary">
              Kitsunee
            </span>
          </div>

          {/* Social Links */}
          <div className="flex space-x-4 items-center">
            <a 
              href="https://github.com/Dovakiin0/Kitsune" 
              target="_blank"
              rel="noopener noreferrer"
              className="p-2 rounded-full hover:bg-accent transition-all duration-300 hover:scale-110"
            >
              <GitHubLogoIcon suppressHydrationWarning width="28" height="28" />
            </a>
            <a 
              href="https://discord.gg/6yAJ3XDHTt" 
              target="_blank"
              rel="noopener noreferrer"
              className="p-2 rounded-full hover:bg-accent transition-all duration-300 hover:scale-110"
            >
              <DiscordLogoIcon suppressHydrationWarning width="28" height="28" />
            </a>
          </div>

          <Separator className="max-w-md" />

          {/* Disclaimer */}
          <p className="text-sm text-muted-foreground text-center max-w-2xl leading-relaxed">
            Kitsune does not store any files on the server, we only link to the
            media which is hosted on 3rd party services.
          </p>

          {/* Copyright */}
          <p className="text-sm text-muted-foreground">
            &copy; {new Date().getFullYear()} Kitsune. All rights reserved.
          </p>
        </div>
      </Container>
    </footer>
  );
};

export default Footer;
