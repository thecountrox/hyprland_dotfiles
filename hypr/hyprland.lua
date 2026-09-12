-- Hyprland 0.55+ configuration. The previous Hyprlang files remain in config/
-- as an untouched reference during the transition.

local config_dir = os.getenv("HOME") .. "/.config/hypr/lua/"
local colors = dofile(config_dir .. "colors.lua")
local apps = dofile(config_dir .. "applications.lua")

dofile(config_dir .. "environment.lua")()
dofile(config_dir .. "settings.lua")(colors)
dofile(config_dir .. "animations.lua")()
dofile(config_dir .. "monitor.lua")()
dofile(config_dir .. "rules.lua")(colors, apps)
dofile(config_dir .. "binds.lua")(apps)
dofile(config_dir .. "autostart.lua")()
