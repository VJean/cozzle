#[macro_use] extern crate conrod_core;
extern crate conrod_glium;
#[macro_use] extern crate conrod_winit;
extern crate find_folder;
extern crate glium;
extern crate image;

use glium::Surface;
use conrod_core::color::Color;

use rand::prelude::*;


mod support;

fn generate_gradient() -> Vec<Color> {
    let mut rng = rand::thread_rng();
    let first_color = Color::Rgba(rng.gen(), rng.gen(), rng.gen(), 1.0);
    let last_color = Color::Rgba(rng.gen(), rng.gen(), rng.gen(), 1.0);

    let mut grad = Vec::new();
    grad.push(first_color);
    let r_step = ( last_color.red() - first_color.red() ) / 10.0;
    let g_step = ( last_color.green() - first_color.green() ) / 10.0;
    let b_step = ( last_color.blue() - first_color.blue() ) / 10.0;
    for n in 2..10 {
        let r = r_step * n as f32;
        let g = g_step * n as f32;
        let b = b_step * n as f32;
        grad.push(Color::Rgba(r + first_color.red(), g + first_color.green(), b + first_color.blue(), 1.0));
    }
    grad.push(last_color);

    grad
}

fn shuffled_gradient(g: & Vec<Color>) -> Vec<Color> {
    let mut rng = rand::thread_rng();
    let mut result = g.clone();
    // don't shuffle first and last elements
    let len = result.len();
    (&mut result[1..len-1]).shuffle(&mut rng);

    result
}

fn main() {
    const WIDTH: u32 = 800;
    const HEIGHT: u32 = 600;

    // Build the window.
    let mut events_loop = glium::glutin::EventsLoop::new();
    let window = glium::glutin::WindowBuilder::new()
        .with_title("Cozzle")
        .with_dimensions((WIDTH, HEIGHT).into());
    let context = glium::glutin::ContextBuilder::new()
        .with_vsync(true)
        .with_multisampling(4);
    let display = glium::Display::new(window, context, &events_loop).unwrap();
    let display = support::GliumDisplayWinitWrapper(display);

    // construct our `Ui`.
    let mut ui = conrod_core::UiBuilder::new([WIDTH as f64, HEIGHT as f64]).build();

    // A type used for converting `conrod_core::render::Primitives` into `Command`s that can be used
    // for drawing to the glium `Surface`.
    let mut renderer = conrod_glium::Renderer::new(&display.0).unwrap();

    // The image map describing each of our widget->image mappings (in our case, none).
    let image_map = conrod_core::image::Map::<glium::texture::Texture2d>::new();

    // Instantiate the generated list of widget identifiers.
    let ids = &mut Ids::new(ui.widget_id_generator());

    // base gradient
    let mut base_gradient = generate_gradient();
    // shuffled gradient
    let mut gradient = shuffled_gradient(&base_gradient);

    // index of selected cell in the gradient
    let mut selected : Option<usize> = None;

    // ends when base gradient == shuffled

    // Poll events from the window.
    let mut event_loop = support::EventLoop::new();
    'main: loop {

        // Handle all events.
        for event in event_loop.next(&mut events_loop) {

            // Use the `winit` backend feature to convert the winit event to a conrod one.
            if let Some(event) = support::convert_event(event.clone(), &display) {
                ui.handle_event(event);
                event_loop.needs_update();
            }

            match event {
                glium::glutin::Event::WindowEvent { event, .. } => match event {
                    // Break from the loop upon `Escape`.
                    glium::glutin::WindowEvent::CloseRequested |
                    glium::glutin::WindowEvent::KeyboardInput {
                        input: glium::glutin::KeyboardInput {
                            virtual_keycode: Some(glium::glutin::VirtualKeyCode::Escape),
                            ..
                        },
                        ..
                    } => break 'main,
                    _ => (),
                },
                _ => (),
            }
        }

        if base_gradient == gradient {
            // generate new gradient
            base_gradient = generate_gradient();
            // shuffled gradient
            gradient = shuffled_gradient(&base_gradient);
        }

        // Instantiate all widgets in the GUI.
        // pass the colors of the buttons (shuffled gradient)
        set_widgets(ui.set_widgets(), ids, gradient.as_mut_slice(), &mut selected);

        // Render the `Ui` and then display it on the screen.
        if let Some(primitives) = ui.draw_if_changed() {
            renderer.fill(&display.0, primitives, &image_map);
            let mut target = display.0.draw();
            target.clear_color(0.0, 0.0, 0.0, 1.0);
            renderer.draw(&display.0, &mut target, &image_map).unwrap();
            target.finish().unwrap();
        }
    }
}

// Button matrix dimensions.
const ROWS: usize = 1;
const COLS: usize = 10;

// Draw the Ui.
fn set_widgets(ref mut ui: conrod_core::UiCell, ids: &mut Ids, colors: &mut [Color], selected: &mut Option<usize>) {
    use conrod_core::{widget, Colorable, Positionable, Sizeable, Widget};

    // Construct our main `Canvas` tree.
    widget::Canvas::new().set(ids.master, ui);

    let master_wh = ui.wh_of(ids.master).unwrap();
    let mut elements = widget::Matrix::new(COLS, ROWS)
        .w_h(master_wh[0], master_wh[1] * 2.0)
        .mid_top_of(ids.master)
        .set(ids.matrix, ui);

    while let Some(elem) = elements.next(ui) {
        let (r, c) = (elem.row, elem.col);
        let n = c + r * c;
        let button = widget::Button::new().color(colors[n]).hover_color(colors[n]);
        for _click in elem.set(button, ui) {
            // Prevent selecting first and last

            // if another already selected and not self, then swap
            // else select for swap
            match selected {
                None => *selected = Some(n),
                Some(id) => {
                    colors.swap(n, *id);
                    *selected = None;
                },
            };
        }
    }
}

// Generate a unique `WidgetId` for each widget.
widget_ids! {
    struct Ids {
        master,
        matrix,
    }
}
