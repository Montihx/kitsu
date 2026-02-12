import React from "react";
import Avatar from "./common/avatar";
import { IAuth } from "@/store/auth-store";
import { Popover, PopoverContent, PopoverTrigger } from "./ui/popover";
import Link from "next/link";
import { User, LogOut } from "lucide-react";
import { api } from "@/lib/api";

type Props = {
  auth: IAuth | null;
  clearAuth: () => void;
};

function NavbarAvatar({ auth, clearAuth }: Props) {
  const [open, setOpen] = React.useState(false);
  const profileSlug = auth?.username || auth?.email || "me";

  return (
    auth && (
      <Popover open={open} onOpenChange={setOpen}>
        <PopoverTrigger>
          <Avatar
            username={auth.username || auth.email}
            url={auth.avatar}
          />
        </PopoverTrigger>
        <PopoverContent className="bg-black bg-opacity-50 backdrop-blur-sm w-[200px] mt-4 mr-4 text-sm flex flex-col space-y-2">
          <div className="mb-2">
            <p>
              Hello,{" "}
              <span className="text-red-500">
                @{auth.username || auth.email}
              </span>
            </p>
          </div>
          <div className="border-b border-gray-600 pb-2">
            <Link
              href={`/profile/${profileSlug}`}
              className="flex flex-row space-x-2 items-center"
              onClick={() => setOpen(false)}
            >
              <User size="20" />
              <p>Profile</p>
            </Link>
          </div>

          <div
            className="flex flex-row space-x-2 items-center cursor-pointer "
            onClick={() => {
              if (auth?.refreshToken) {
                api
                  .post("/auth/logout", {
                    refresh_token: auth.refreshToken,
                  })
                  .catch(() => {});
              }
              clearAuth();
            }}
          >
            <LogOut size="20" />
            <p>Logout</p>
          </div>
        </PopoverContent>
      </Popover>
    )
  );
}

export default NavbarAvatar;
