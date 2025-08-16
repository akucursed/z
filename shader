-- Standalone Shader Script
-- Применяет настройки шейдера без GUI

local game = game
local workspace = workspace
local lighting = game:GetService("Lighting")
local terrain = workspace.Terrain
local runService = game:GetService("RunService")
local players = game:GetService("Players")
local localPlayer = players.LocalPlayer
local camera = workspace.CurrentCamera

-- Настройки из твоего сохранения
local savedSettings = {
 ["Skybox"]={
  ["rt"]="\x72\x62\x78\x61\x73\x73\x65\x74\x69\x64\x3A\x2F\x2F\x34\x34\x39\x38\x38\x33\x30\x34\x31\x37",
  ["dn"]="\x72\x62\x78\x61\x73\x73\x65\x74\x69\x64\x3A\x2F\x2F\x34\x34\x39\x38\x38\x32\x38\x38\x31\x32",
  ["up"]="\x72\x62\x78\x61\x73\x73\x65\x74\x69\x64\x3A\x2F\x2F\x34\x34\x39\x38\x38\x33\x31\x37\x34\x36",
  ["bk"]="\x72\x62\x78\x61\x73\x73\x65\x74\x69\x64\x3A\x2F\x2F\x34\x34\x39\x38\x38\x32\x38\x33\x38\x32",
  ["ft"]="\x72\x62\x78\x61\x73\x73\x65\x74\x69\x64\x3A\x2F\x2F\x34\x34\x39\x38\x38\x32\x39\x39\x31\x37",
  ["lt"]="\x72\x62\x78\x61\x73\x73\x65\x74\x69\x64\x3A\x2F\x2F\x34\x34\x39\x38\x38\x33\x30\x39\x31\x31",
 },
 ["Bloom"]={
  [1]=true,
  [2]=0.72,
  [3]=8.96,
  [4]=2.72,
 },
 ["Depth Of Field"]={
  [1]=false,
  [2]=0.217,
  [3]=11.54,
  [4]=16.77,
  [5]=0.277,
 },
 ["Shader"]={
  ["hbjhd"]=0.277,
  ["sdkvkflv"]=16.77,
  ["gyhgtg"]=0.46,
  ["fvgsdfg"]=11.54,
  ["fvrtccvghghj"]=Color3.new(0.784314, 0.784314, 0.784314),
  ["jddfjsd"]=0.6,
  ["sdfcddc"]=0.25,
  ["jdfkd"]=0.217,
  ["tfbghuugbnjhg"]=-0.44,
  ["jnfdhbnfcvh"]=0.72,
  ["hdfr7thgr"]=0.5,
  ["skdjfkdm"]=0.46,
  ["khnbfth"]=0.25,
  ["hyhnngtf"]=Color3.new(0, 0, 0),
  ["sejfd"]=0xA,
  ["efjdjfk"]=Color3.new(0.631373, 0.647059, 0.635294),
  ["ygbhnj"]=2.72,
  ["sjdjncdjf"]=Color3.new(0.631373, 0.647059, 0.635294),
  ["ugtbbjhygt"]=0.48,
  ["shdbsnjfc"]=0.28,
  ["ghuybhuyhj"]=0x24,
  ["hgnujuu7thgr"]=true,
  ["fhnchvhfjsd"]=0.12,
  ["ygbhggv"]=0.48,
  ["yfbghj"]=Color3.new(0.427451, 0.431373, 0.423529),
  ["njnfg"]=0x5,
  ["tgvbyd"]=14.4,
  ["hgyghkg"]=Color3.new(0, 0, 0),
  ["yfbhjku"]=Color3.new(0, 0, 0),
  ["fvtyghj"]=8.96,
  ["jghbjhgyfd"]=Color3.new(0.631373, 0.647059, 0.635294),
  ["ygyyfgvhbjytrt"]=0.203,
 },
 ["SunFlare"]=true,
 ["Blur Motion"]=false,
 ["Time"]={
  [1]=14.4,
  [2]=0x24,
 },
 ["Blur Effects"]=false,
 ["Atmosphere"]={
  [1]=0.28,
  [2]=0.46,
  [3]=0xA,
  [4]=0.6,
 },
 ["ColorCorrection"]={
  [1]=true,
  [2]=0.12,
  [3]=0.48,
  [4]=-0.44,
 },
 ["Sunrays"]={
  [1]=true,
  [2]=0.07999999821186066,
  [3]=0x1,
 },
 ["Clouds"]={
  [1]=0.46,
  [2]=0.48,
 },
}

-- Функция для декодирования hex строк
local function decodeHexString(str)
    return str:gsub("\\x(%x%x)", function(h)
        return string.char(tonumber(h, 16))
    end)
end

-- Функция для создания эффектов
local function createEffect(effectType)
    local effect = lighting:FindFirstChildOfClass(effectType)
    if effect then
        -- Проверяем, есть ли у эффекта свойство Enabled через pcall
        local success = pcall(function()
            effect.Enabled = false
        end)
        local newEffect = effect:Clone()
        newEffect.Parent = lighting
        if success then
            newEffect.Enabled = true
        end
        return newEffect
    else
        local newEffect = Instance.new(effectType)
        newEffect.Parent = lighting
        return newEffect
    end
end

-- Создание эффектов
local bloom = createEffect("BloomEffect")
local depthOfField = createEffect("DepthOfFieldEffect")
local colorCorrection = createEffect("ColorCorrectionEffect")
local sunRays = createEffect("SunRaysEffect")
local blur = createEffect("BlurEffect")
local atmosphere = createEffect("Atmosphere")
local sky = createEffect("Sky")

-- Создание облаков
local clouds = terrain:FindFirstChildOfClass("Clouds")
if not clouds then
    clouds = Instance.new("Clouds")
    clouds.Parent = terrain
end

-- Применение настроек Bloom
bloom.Enabled = savedSettings["Bloom"][1]
bloom.Intensity = savedSettings["Bloom"][2]
bloom.Size = savedSettings["Bloom"][3]
bloom.Threshold = savedSettings["Bloom"][4]

-- Применение настроек Depth of Field
depthOfField.Enabled = savedSettings["Depth Of Field"][1]
depthOfField.FarIntensity = savedSettings["Depth Of Field"][2]
depthOfField.FocusDistance = savedSettings["Depth Of Field"][3]
depthOfField.InFocusRadius = savedSettings["Depth Of Field"][4]
depthOfField.NearIntensity = savedSettings["Depth Of Field"][5]

-- Применение настроек Color Correction
colorCorrection.Enabled = savedSettings["ColorCorrection"][1]
colorCorrection.Brightness = savedSettings["ColorCorrection"][2]
colorCorrection.Contrast = savedSettings["ColorCorrection"][3]
colorCorrection.Saturation = savedSettings["ColorCorrection"][4]
colorCorrection.TintColor = savedSettings["Shader"]["fvrtccvghghj"]

-- Применение настроек Sun Rays
sunRays.Enabled = savedSettings["Sunrays"][1]
sunRays.Intensity = savedSettings["Sunrays"][2]
sunRays.Spread = savedSettings["Sunrays"][3]

-- Применение настроек Blur
blur.Enabled = savedSettings["Blur Effects"]
blur.Size = savedSettings["Shader"]["njnfg"]

-- Применение настроек Atmosphere
atmosphere.Density = savedSettings["Atmosphere"][1]
atmosphere.Offset = savedSettings["Atmosphere"][2]
atmosphere.Glare = savedSettings["Atmosphere"][3]
atmosphere.Haze = savedSettings["Atmosphere"][4]
atmosphere.Color = savedSettings["Shader"]["sjdjncdjf"]
atmosphere.Decay = savedSettings["Shader"]["efjdjfk"]

-- Применение настроек Clouds
clouds.Cover = savedSettings["Clouds"][1]
clouds.Density = savedSettings["Clouds"][2]
clouds.Color = savedSettings["Shader"]["jghbjhgyfd"]

-- Применение настроек Lighting
lighting.Ambient = savedSettings["Shader"]["yfbghj"]
lighting.ClockTime = savedSettings["Shader"]["tgvbyd"]
lighting.GeographicLatitude = savedSettings["Shader"]["ghuybhuyhj"]
lighting.Brightness = savedSettings["Shader"]["khnbfth"]
lighting.ColorShift_Bottom = savedSettings["Shader"]["hgyghkg"]
lighting.ColorShift_Top = savedSettings["Shader"]["yfbhjku"]
lighting.EnvironmentDiffuseScale = savedSettings["Shader"]["ygyyfgvhbjytrt"]
lighting.EnvironmentSpecularScale = savedSettings["Shader"]["sdfcddc"]
lighting.GlobalShadows = savedSettings["Shader"]["hgnujuu7thgr"]
lighting.OutdoorAmbient = savedSettings["Shader"]["hyhnngtf"]
lighting.ExposureCompensation = savedSettings["Shader"]["hdfr7thgr"]

-- Применение настроек Skybox
local skybox = savedSettings["Skybox"]
sky.SkyboxBk = decodeHexString(skybox["bk"])
sky.SkyboxDn = decodeHexString(skybox["dn"])
sky.SkyboxFt = decodeHexString(skybox["ft"])
sky.SkyboxLf = decodeHexString(skybox["lt"])
sky.SkyboxRt = decodeHexString(skybox["rt"])
sky.SkyboxUp = decodeHexString(skybox["up"])

-- Логика SunFlare
local sunFlareEnabled = savedSettings["SunFlare"]
if sunFlareEnabled then
    -- Создание ScreenGui для SunFlare
    local screenGui = Instance.new("ScreenGui")
    screenGui.Name = "SunFlareGui"
    screenGui.Parent = localPlayer.PlayerGui
    screenGui.ResetOnSpawn = false
    -- Основной флейр
    local mainFlare = Instance.new("ImageLabel")
    mainFlare.Name = "MainFlare"
    mainFlare.Size = UDim2.new(0, 200, 0, 200)
    mainFlare.BackgroundTransparency = 1
    mainFlare.Image = "rbxassetid://277033149"
    mainFlare.ImageColor3 = Color3.new(1, 1, 0.95)
    mainFlare.ZIndex = 0
    mainFlare.Parent = screenGui
    
    -- Дополнительные флейры
    local flareDistances = {1.7, 0.3, -0.3, -0.9}
    local flareSizes = {0.7, 0.2, 1.2, 0.45}
    local flareTransparencies = {0.8, 0.7, 0.9, 0.6}
    
    for i = 1, #flareDistances do
        local flare = Instance.new("ImageLabel")
        flare.Name = "Flare" .. i
        flare.Size = UDim2.new(0, flareSizes[i] * 40, 0, flareSizes[i] * 40)
        flare.BackgroundTransparency = 1
        flare.ImageTransparency = flareTransparencies[i]
        flare.Image = "rbxassetid://15164863822"
        flare.ImageColor3 = Color3.new(1, 1, 0.8)
        flare.ZIndex = -1
        flare.Parent = screenGui
    end
    
    -- Функция обновления позиции флейров
    local function updateFlarePosition()
        local sunDirection = lighting:GetSunDirection()
        local sunScreenPos = camera:WorldToScreenPoint(camera.CFrame.Position + sunDirection * 1000)
        
        if sunScreenPos.Z > 0 then
            local center = camera.ViewportSize / 2
            local sunPos = Vector2.new(sunScreenPos.X, sunScreenPos.Y)
            local direction = sunPos - center
            
            -- Позиция основного флейра
            mainFlare.Position = UDim2.new(0, sunPos.X - mainFlare.AbsoluteSize.X/2, 0, sunPos.Y - mainFlare.AbsoluteSize.Y/2)
            mainFlare.Visible = true
            
            -- Позиции дополнительных флейров
            for i = 1, #flareDistances do
                local flare = screenGui:FindFirstChild("Flare" .. i)
                if flare then
                    local flarePos = center + direction * flareDistances[i]
                    flare.Position = UDim2.new(0, flarePos.X - flare.AbsoluteSize.X/2, 0, flarePos.Y - flare.AbsoluteSize.Y/2)
                    flare.Visible = true
                end
            end
        else
            mainFlare.Visible = false
            for i = 1, #flareDistances do
                local flare = screenGui:FindFirstChild("Flare" .. i)
                if flare then
                    flare.Visible = false
                end
            end
        end
    end
    
    -- Подключение обновления позиции
    runService.RenderStepped:Connect(updateFlarePosition)
end

-- Логика Motion Blur
local motionBlurEnabled = savedSettings["Blur Motion"]
if motionBlurEnabled then
    local motionBlur = Instance.new("BlurEffect")
    motionBlur.Size = 26
    motionBlur.Parent = camera
    
    local lastLookVector = camera.CFrame.LookVector
    local motionBlurMultiplier = 11
    local motionBlurExponent = 5
    
         runService.RenderStepped:Connect(function()
         local currentLookVector = camera.CFrame.LookVector
         local magnitude = (currentLookVector - lastLookVector).Magnitude
         motionBlur.Size = math.abs(magnitude) * motionBlurMultiplier * motionBlurExponent / 2
         lastLookVector = currentLookVector
     end)
end
