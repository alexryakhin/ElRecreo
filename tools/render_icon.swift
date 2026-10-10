// Renders the app icon's layers (ElRecreo/Resources/AppIcon.icon) as a flat PNG for the website.
// usage: swift tools/render_icon.swift <out.png> <size> <top hex> <bottom hex> <rounded|square> <layer.svg>...
// Layers are drawn in order, so list them bottom first (sun, gourd, virola, bombilla).
import AppKit

let a = CommandLine.arguments
let out = a[1], size = CGFloat(Double(a[2])!), top = a[3], bottom = a[4], rounded = a[5] == "rounded"
func color(_ h: String) -> NSColor {
    var v: UInt64 = 0; Scanner(string: h).scanHexInt64(&v)
    return NSColor(srgbRed: CGFloat((v >> 16) & 255) / 255, green: CGFloat((v >> 8) & 255) / 255, blue: CGFloat(v & 255) / 255, alpha: 1)
}
let rep = NSBitmapImageRep(bitmapDataPlanes: nil, pixelsWide: Int(size), pixelsHigh: Int(size), bitsPerSample: 8, samplesPerPixel: 4,
                           hasAlpha: true, isPlanar: false, colorSpaceName: .deviceRGB, bytesPerRow: 0, bitsPerPixel: 0)!
NSGraphicsContext.saveGraphicsState()
NSGraphicsContext.current = NSGraphicsContext(bitmapImageRep: rep)
let rect = NSRect(x: 0, y: 0, width: size, height: size)
if rounded { NSBezierPath(roundedRect: rect, xRadius: size * 0.2237, yRadius: size * 0.2237).addClip() }
NSGradient(starting: color(top), ending: color(bottom))!.draw(in: rect, angle: -90)
for layer in a.dropFirst(6) { NSImage(contentsOfFile: layer)!.draw(in: rect) }
NSGraphicsContext.restoreGraphicsState()
try! rep.representation(using: .png, properties: [:])!.write(to: URL(fileURLWithPath: out))
