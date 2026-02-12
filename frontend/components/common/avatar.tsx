import React from "react";
import {
  Avatar as AvatarCN,
  AvatarFallback,
  AvatarImage,
} from "@/components/ui/avatar";
import { PLACEHOLDER_POSTER } from "@/utils/constants";

type Props = {
  url?: string;
  username?: string;
  className?: string;
  onClick?: () => void;
};

function Avatar({
  url,
  username,
  className,
  onClick,
}: Props) {
  const src = url || PLACEHOLDER_POSTER;

  return (
    <AvatarCN className={className} onClick={onClick}>
      <AvatarImage src={src} alt={username} />
      <AvatarFallback>
        {username?.charAt(0).toUpperCase()}
        {username?.charAt(1).toLowerCase()}
      </AvatarFallback>
    </AvatarCN>
  );
}

export default Avatar;
