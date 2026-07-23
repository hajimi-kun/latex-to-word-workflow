-- Keep this filter semantic: use it only for distinctions that would be lost
-- before DOCX post-processing. Do not construct Word fields or bookmarks here.

local prose_math = {
  -- ["\\mathrm{CO_2}"] = {"CO", "2", "subscript"},
}

function Math(el)
  if el.mathtype ~= "InlineMath" then return nil end
  local replacement = prose_math[el.text]
  if not replacement then return nil end
  if replacement[3] == "subscript" then
    return {pandoc.Str(replacement[1]), pandoc.Subscript({pandoc.Str(replacement[2])})}
  end
  return pandoc.Str(replacement[1])
end
