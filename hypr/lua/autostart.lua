return function()
    hl.on("hyprland.start", function()
        -- The cursor manager is initialized before config environment variables.
        -- Apply the selected cursor explicitly once Hyprland's IPC is available.
        hl.exec_cmd("$HOME/.local/opt/hyprland-tearing-test/bin/hyprctl setcursor Hackneyed 22")
        hl.exec_cmd("swaybg -o \\* -i /usr/share/wallpapers/cachyos-wallpapers/jellyfish.jpg -m fill")
        hl.exec_cmd("$HOME/.local/bin/waybar")
        hl.exec_cmd("mako")
        hl.exec_cmd('bash -c "mkfifo /tmp/$HYPRLAND_INSTANCE_SIGNATURE.wob && tail -f /tmp/$HYPRLAND_INSTANCE_SIGNATURE.wob | wob -c ~/.config/hypr/wob.ini & disown"')
        hl.exec_cmd("/usr/lib/hyprpolkitagent/hyprpolkitagent")
        hl.exec_cmd("wlsunset -l 13.00444 -L 80.25833 -t 4300 -T 6500")
        -- Let Vicinae follow the XDG desktop-portal color scheme rather than
        -- this session's qt5ct default, which is fixed to dark.
        hl.exec_cmd("QT_QPA_PLATFORMTHEME=xdgdesktopportal vicinae server")
        hl.exec_cmd("systemctl --user import-environment")
        hl.exec_cmd("dbus-update-activation-environment --systemd")
        hl.exec_cmd("hypridle")
    end)
end
