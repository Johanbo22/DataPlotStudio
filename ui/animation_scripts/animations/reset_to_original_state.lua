-- Animation that is played when the user clicks the reset to original state button in DataTab

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

    -- Label
    table.insert(positions, {
        type = "text",
        text = "Reset to Original",
        x = 0,
        y = -60
    })

    if eased < 0.35 then
        local radius = 25
        local arc = eased / 0.35

        for i = 0, arc, 0.15 do
            local angle = i * 2 * math.pi
            table.insert(positions, {
                type = "circle",
                x = math.cos(angle) * radius,
                y = math.sin(angle) * radius
            })
        end
    else
        local t = (eased - 0.35) / 0.65
        local radius = 25

        for i = 0, math.min(t, 1), 0.1 do
            local angle = (1 - i) * 1.5 * math.pi
            table.insert(positions, {
                type = "circle",
                x = math.cos(angle) * radius,
                y = math.sin(angle) * radius
            })
        end

        if t > 0.6 then
            local s = math.min((t - 0.6) / 0.4, 1)

            table.insert(positions, {
                type = "line",
                x1 = -radius * 0.7,
                y1 = -radius * 0.1,
                x2 = -radius * 0.9 * s,
                y2 = -radius * 0.35 * s
            })

            table.insert(positions, {
                type = "line",
                x1 = -radius * 0.7,
                y1 = -radius * 0.1,
                x2 = -radius * 0.45 * s,
                y2 = -radius * 0.35 * s
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
