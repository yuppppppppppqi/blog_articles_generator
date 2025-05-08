<?php
/**
 * GeneratePress Child Theme functions and definitions
 *
 * @link https://developer.wordpress.org/themes/basics/theme-functions/
 *
 * @package GeneratePress_Child
 */

add_action( 'wp_enqueue_scripts', 'generatepress_child_enqueue_styles' );
function generatepress_child_enqueue_styles() {
    wp_enqueue_style( 'generatepress-parent-style', get_template_directory_uri() . '/style.css' );
    // If you want to add your own child theme stylesheet, uncomment the next line
    // wp_enqueue_style( 'generatepress-child-style', get_stylesheet_directory_uri() . '/style.css', array( 'generatepress-parent-style' ), wp_get_theme()->get('Version') );
}

/**
 * Set Polylang language for a post via REST API and link translations.
 * Expects 'polylang_lang_code' in the JSON request body with the language slug (e.g., 'ja', 'en').
 * Optionally expects 'polylang_translations' as an associative array { <original_lang_slug>: <original_post_id> } to link translations.
 */
function my_set_polylang_language_and_translations_on_rest_insert( $post, $request, $creating ) {
    if ( ! function_exists( 'pll_set_post_language' ) || ! function_exists( 'pll_languages_list' ) || ! function_exists( 'pll_save_post_translations' ) || ! function_exists('pll_get_post_language') ) {
        error_log("Polylang Hook: Core Polylang functions not available.");
        return;
    }

    $params = $request->get_json_params();
    $post_id = $post->ID;
    $available_polylang_slugs = pll_languages_list( array( 'fields' => 'slug' ) );

    // 1. Set post language
    $lang_slug_to_set = null;
    if ( isset( $params['polylang_lang_code'] ) && is_string( $params['polylang_lang_code'] ) ) {
        $temp_lang_slug = sanitize_text_field( $params['polylang_lang_code'] );
        if ( ! empty( $temp_lang_slug ) && in_array( $temp_lang_slug, $available_polylang_slugs, true ) ) {
            pll_set_post_language( $post_id, $temp_lang_slug );
            $lang_slug_to_set = $temp_lang_slug;
            error_log( "Polylang Hook: Language '{$lang_slug_to_set}' set for post ID {$post_id}." );
        } else {
            error_log( "Polylang Hook: Invalid or empty 'polylang_lang_code' ('{$temp_lang_slug}') for post ID {$post_id}." );
        }
    }

    // 2. Link translations
    if ( $lang_slug_to_set && isset( $params['polylang_translations'] ) && is_array( $params['polylang_translations'] ) ) {
        $translations_from_request = $params['polylang_translations'];
        $translations_to_save = array();

        // Add the current post to the translations array
        $translations_to_save[$lang_slug_to_set] = $post_id;
        error_log("Polylang Hook: Preparing to save translations for post ID {$post_id} ({$lang_slug_to_set}). Current post added.");

        foreach ( $translations_from_request as $original_lang_slug => $original_post_id ) {
            $original_lang_slug = sanitize_text_field( $original_lang_slug );
            $original_post_id = intval( $original_post_id );

            if ( $original_post_id > 0 && in_array( $original_lang_slug, $available_polylang_slugs, true ) ) {
                // Ensure the original post actual language matches the provided slug, if possible
                $actual_original_lang = pll_get_post_language($original_post_id, 'slug');
                if ($actual_original_lang === $original_lang_slug) {
                    $translations_to_save[$original_lang_slug] = $original_post_id;
                    error_log("Polylang Hook: Added original post ID {$original_post_id} ({$original_lang_slug}) to translations for post ID {$post_id}.");
                } else {
                    error_log("Polylang Hook: Mismatch language for original post ID {$original_post_id}. Expected '{$original_lang_slug}', got '{$actual_original_lang}'. Skipping.");
                }
            } else {
                error_log("Polylang Hook: Invalid original post ID ({$original_post_id}) or lang slug ('{$original_lang_slug}') in polylang_translations for post ID {$post_id}.");
            }
        }

        if ( count( $translations_to_save ) > 1 ) { // Need at least 2 to link
            pll_save_post_translations( $translations_to_save );
            error_log( "Polylang Hook: Attempted to save translations for post ID {$post_id}: " . print_r( $translations_to_save, true ) );
        } else {
            error_log( "Polylang Hook: Not enough valid translations to save for post ID {$post_id}. Translations array: " . print_r( $translations_to_save, true ) );
        }
    }
}
add_action( 'rest_insert_post', 'my_set_polylang_language_and_translations_on_rest_insert', 20, 3 ); // Priority changed to 20

// add_action( 'rest_insert_page', 'my_set_polylang_language_and_translations_on_rest_insert', 10, 3 );

?> 