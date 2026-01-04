state = {
    progress = 0,
    duration = 0.8,
    complete = false
}

local function ease_out_cubic(t)
    return 1 - (1 - t) ^ 3
end

function update(dt)
    if state.complete then return end

    state.progress = math.min(state.progress + dt / state.duration, 1)
    state.complete = state.progress >= 1
end

function get_frame()
    local eased = ease_out_cubic(state.progress)
    local positions = {}

    table.insert(positions, {
        type = "text",
        text = "Project Saved",
        x = 0,
        y = -60
    })

    if eased < 0.3 then
        local radius = 25 * (eased / 0.3)

        for i = 0, 1, 0.2 do
            local angle = i * 2 * math.pi
            table.insert(positions, {
                type = "circle",
                x = math.cos(angle) * radius,
                y = math.sin(angle) * radius
            })
        end
    else
        local t = (eased - 0.3) / 0.7

        if t > 0.3 then
            local s1 = math.min((t - 0.3) / 0.7, 1)
            table.insert(positions, {
                type = "line",
                x1 = -18 * s1,
                y1 = 5 * s1,
                x2 = -8,
                y2 = 18
            })
        end

        if t > 0.7 then
            local s2 = math.min((t - 0.6) / 0.4, 1)
            table.insert(positions, {
                type = "line",
                x1 = -8,
                y1 = 18,
                x2 = 15 * s2,
                y2 = -10 + 5 * s2
            })
        end
    end

    return {
        positions = positions,
        complete = state.complete
    }
end

function reset()
    state.progress = 0
    state.complete = false
end
