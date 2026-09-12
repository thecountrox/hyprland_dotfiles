return function(colors)
    hl.config({
        general = {
            allow_tearing = true,
            gaps_in = 3,
            gaps_out = 3,
            border_size = 1,
            col = {
                active_border = "rgb(bd93f9)",
                inactive_border = colors.blue_medium,
            },
            layout = "master",
            snap = {
                enabled = true,
            },
        },
        decoration = {
            active_opacity = 1,
            rounding = 4,
            blur = {
                enabled = true,
                size = 4,
                passes = 2,
                new_optimizations = true,
                ignore_opacity = true,
                xray = true,
                noise = 0.0117,
                contrast = 0.8916,
                brightness = 0.8172,
                vibrancy = 0.1696,
                vibrancy_darkness = 0,
                special = false,
                popups = false,
                popups_ignorealpha = 0.2,
                input_methods = false,
                input_methods_ignorealpha = 0.2,
            },
            shadow = {
                enabled = false,
            },
        },
        input = {
            follow_mouse = 1,
            float_switch_override_focus = 2,
            accel_profile = "flat",
            sensitivity = 0.25,
            kb_options = "caps:swapescape",
        },
        group = {
            col = {
                border_active = colors.green_dark,
                border_inactive = colors.green_light,
                border_locked_active = colors.green_medium,
                border_locked_inactive = colors.blue_dark,
            },
            groupbar = {
                font_family = "Fira Sans",
                text_color = colors.blue_dark,
                col = {
                    active = colors.green_dark,
                    inactive = colors.green_light,
                    locked_active = colors.green_medium,
                    locked_inactive = colors.blue_dark,
                },
            },
        },
        misc = {
            font_family = "Atkinson Hyperlegible",
            splash_font_family = "Atkinson Hyperlegible",
            disable_hyprland_logo = true,
            col = { splash = colors.green_light },
            background_color = colors.blue_dark,
            enable_swallow = true,
            swallow_regex = "^(cachy-browser|zen-browser|nautilus|nemo|thunar|btrfs-assistant.)$",
            focus_on_activate = false,
            vrr = 1,
        },
        render = {
            direct_scanout = 1,
            new_render_scheduling = false,
        },
        cursor = {
            -- Auto-disable the hardware cursor while tearing, avoiding the
            -- hw-cursor transition when a game locks/hides the pointer.
            no_hardware_cursors = 2,
            inactive_timeout = 0,
            hide_on_key_press = false,
        },
        dwindle = {
            special_scale_factor = 0.8,
            preserve_split = true,
        },
        master = {
            new_status = "slave",
            orientation = "left",
            special_scale_factor = 0.8,
            mfact = 0.55,
        },
        binds = {
            allow_workspace_cycles = true,
            workspace_center_on = 1,
            movefocus_cycles_fullscreen = true,
            window_direction_monitor_fallback = true,
        },
        xwayland = {
            force_zero_scaling = true,
        },
    })
end
