if (solved) {
	draw_set_font(font_Flag)
    draw_set_halign(fa_center);
    draw_set_valign(fa_middle);
    draw_set_color(c_red);
	
    draw_text_transformed(display_get_gui_width()/2, display_get_gui_height()/2, flag_str, 1, 1, 0);
	
}
