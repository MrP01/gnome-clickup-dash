/* extension.js
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 *
 * SPDX-License-Identifier: GPL-2.0-or-later
 */

/* exported init */

const { GObject, St, Clutter } = imports.gi;
const ExtensionUtils = imports.misc.extensionUtils;
const Main = imports.ui.main;
const PanelMenu = imports.ui.panelMenu;
const PopupMenu = imports.ui.popupMenu;

const GETTEXT_DOMAIN = "gnome-clickup-dash";
const Gettext = imports.gettext.domain(GETTEXT_DOMAIN);
const _ = Gettext.gettext;

const Chart = GObject.registerClass(
  class Chart extends St.DrawingArea {
    _init() {
      super._init();
      log("The Chart is initialized! :)");

      this.draw();
    }

    draw() {
      // Paint background
      let ctx = this.get_context();
      let backgroundColor = new Clutter.Color({ red: 45, green: 45, blue: 45, alpha: 255 });
      Clutter.cairo_set_source_color(ctx, backgroundColor);
      ctx.rectangle(0, 0, width, height);
      ctx.fill();
    }
  }
);

const Indicator = GObject.registerClass(
  class Indicator extends PanelMenu.Button {
    _init() {
      super._init(0.0, _("My Shiny Indicator"));

      let box = new St.BoxLayout({ style_class: "panel-status-menu-box" });
      box.add_child(
        new St.Icon({
          icon_name: "face-smile-symbolic",
          style_class: "system-status-icon",
        })
      );
      box.add_child(PopupMenu.arrowIcon(St.Side.BOTTOM));
      this.add_child(box);

      let item = new PopupMenu.PopupMenuItem(_("Show Notification"));
      item.connect("activate", () => {
        Main.notify(_("What's up, folks?"));
      });
      this.menu.addMenuItem(item);

      this.chart = new Chart();
      let item2 = new PopupMenu.PopupBaseMenuItem(); // is a BoxLayout itself
      item2.add_child(this.chart);
      this.menu.addMenuItem(item2);
    }
  }
);

class Extension {
  constructor(uuid) {
    this._uuid = uuid;

    ExtensionUtils.initTranslations(GETTEXT_DOMAIN);
  }

  enable() {
    this._indicator = new Indicator();
    Main.panel.addToStatusArea(this._uuid, this._indicator);
  }

  disable() {
    this._indicator.destroy();
    this._indicator = null;
  }
}

function init(meta) {
  return new Extension(meta.uuid);
}
