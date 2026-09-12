return function()
    hl.config({ animations = { enabled = true } })

    hl.curve("myBezier", { type = "bezier", points = { { 0.2, 0 }, { 0, 1 } } })
    hl.curve("easeInOut", { type = "bezier", points = { { 0.83, 0 }, { 0.17, 1 } } })
    hl.curve("rofi_resize", { type = "bezier", points = { { 0.13, 0.99 }, { 0.29, 1.1 } } })

    hl.animation({ leaf = "windows", enabled = true, speed = 4, bezier = "default", style = "popin" })
    hl.animation({ leaf = "windowsOut", enabled = true, speed = 5, bezier = "default", style = "popin 80%" })
    hl.animation({ leaf = "border", enabled = true, speed = 10, bezier = "default" })
    hl.animation({ leaf = "borderangle", enabled = true, speed = 8, bezier = "default" })
    hl.animation({ leaf = "fade", enabled = true, speed = 7, bezier = "default" })
    hl.animation({ leaf = "workspaces", enabled = true, speed = 4, bezier = "default" })
end
