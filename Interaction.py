# user_interaction_manager.py
# Member 5: User Interaction Features (15%)
# Develop user interaction functions, dialog design, menu system

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime

class UserInteractionManager:
    def __init__(self, data_manager):
        self.data_manager = data_manager

    def _center_dialog(self, dialog, parent, w=400, h=300):
        dialog.geometry(f"{w}x{h}+{parent.winfo_rootx()+50}+{parent.winfo_rooty()+50}")
        dialog.transient(parent); dialog.grab_set(); dialog.resizable(False, False)

    def show_add_transaction_dialog(self, parent):
        d = tk.Toplevel(parent); d.title("Add Transaction Record"); self._center_dialog(d, parent, 450, 400)
        f = ttk.Frame(d, padding=25); f.pack(fill='both', expand=True)

        date_var = tk.StringVar(value=datetime.now().strftime('%Y-%m-%d'))
        type_var, category_var, amount_var, desc_var, tags_var = (tk.StringVar(value='expense'), tk.StringVar(), tk.StringVar(), tk.StringVar(), tk.StringVar())

        def update_categories(*_):
            category_combo['values'] = self.data_manager.data['categories'][type_var.get()]; category_var.set('')
        def update_preview(*_):
            preview.config(state='normal'); preview.delete('1.0', 'end')
            preview.insert('1.0', f"Date: {date_var.get()}\nType: {type_var.get().title()}\nCategory: {category_var.get()}\nAmount: ${amount_var.get() or '0.00'}\nDescription: {desc_var.get()}"); preview.config(state='disabled')
        def save():
            try:
                if not all([date_var.get(), type_var.get(), category_var.get(), amount_var.get(), desc_var.get()]):
                    return messagebox.showerror("Error", "Please fill in all required fields")
                amt = float(amount_var.get()); assert amt > 0
                datetime.strptime(date_var.get(), '%Y-%m-%d')
                if self.data_manager.add_transaction({'date': date_var.get(), 'type': type_var.get(), 'category': category_var.get(), 'amount': amt, 'description': desc_var.get(), 'tags': tags_var.get().split(',') if tags_var.get() else []}):
                    messagebox.showinfo("Success", "Transaction added!"); d.destroy()
            except ValueError:
                messagebox.showerror("Error", "Enter valid amount/date")
            except AssertionError:
                messagebox.showerror("Error", "Amount must be > 0")
        def clear():
            date_var.set(datetime.now().strftime('%Y-%m-%d')); type_var.set('expense'); category_var.set(''); amount_var.set(''); desc_var.set(''); tags_var.set('')

        entries = [("Date:", date_var), ("Type:", type_var), ("Category:", category_var), ("Amount ($):", amount_var), ("Description:", desc_var), ("Tags (optional):", tags_var)]
        for i, (lbl, var) in enumerate(entries):
            ttk.Label(f, text=lbl).grid(row=i, column=0, sticky='w', pady=5)
            if lbl == "Type:":
                widget = ttk.Combobox(f, textvariable=var, state="readonly", values=('income','expense'))
                widget.bind('<<ComboboxSelected>>', update_categories)
            elif lbl == "Category:":
                category_combo = ttk.Combobox(f, textvariable=var, state="readonly"); update_categories()
                widget = category_combo
                ttk.Button(f, text="+", width=3, command=lambda:self.show_add_category_dialog(d, type_var.get(), category_combo, category_var)).grid(row=i, column=2, padx=5)
            else:
                widget = ttk.Entry(f, textvariable=var, width=30)
            widget.grid(row=i, column=1, padx=(10,0), sticky='ew')
            var.trace('w', update_preview)

        preview = tk.Text(ttk.LabelFrame(f, text="Preview", padding=10), height=3, width=40, bg='#f0f0f0', state='disabled'); preview.master.grid(row=7, column=0, columnspan=3, pady=15, sticky='ew'); preview.pack(fill='x')

        btnf = ttk.Frame(f); btnf.grid(row=8, column=0, columnspan=3, pady=20)
        for txt, cmd in [("Save", save), ("Clear", clear), ("Cancel", d.destroy)]: ttk.Button(btnf, text=txt, command=cmd).pack(side='left', padx=5)
        f.columnconfigure(1, weight=1); update_preview(); return d

    def show_date_picker(self, parent, date_var):
        d = tk.Toplevel(parent); d.title("Select Date"); self._center_dialog(d, parent, 300, 200)
        f = ttk.Frame(d, padding=20); f.pack(fill='both', expand=True)
        year, month, day = (tk.IntVar(value=datetime.now().year), tk.IntVar(value=datetime.now().month), tk.IntVar(value=datetime.now().day))
        for i,(lbl,var,lo,hi) in enumerate([("Year:",year,2000,2030),("Month:",month,1,12),("Day:",day,1,31)]):
            ttk.Label(f,text=lbl).grid(row=i,column=0,sticky='w'); ttk.Spinbox(f,from_=lo,to=hi,textvariable=var,width=10).grid(row=i,column=1,padx=(10,0))
        def set_date():
            try:
                date_var.set(f"{year.get():04d}-{month.get():02d}-{day.get():02d}"); datetime.strptime(date_var.get(), '%Y-%m-%d'); d.destroy()
            except ValueError: messagebox.showerror("Error","Invalid date")
        btnf = ttk.Frame(f); btnf.grid(row=3,column=0,columnspan=2,pady=20)
        ttk.Button(btnf,text="Set Date",command=set_date).pack(side='left',padx=5)
        ttk.Button(btnf,text="Cancel",command=d.destroy).pack(side='left',padx=5)

    def show_add_category_dialog(self, parent, category_type, category_combo, category_var):
        d = tk.Toplevel(parent); d.title(f"Add {category_type.title()} Category"); self._center_dialog(d, parent, 350, 150)
        f = ttk.Frame(d, padding=20); f.pack(fill='both', expand=True)
        name_var = tk.StringVar(); ttk.Label(f,text="Category Name:").grid(row=0,column=0,sticky='w'); e=ttk.Entry(f,textvariable=name_var,width=30); e.grid(row=0,column=1,padx=(10,0)); e.focus()
        def add():
            name=name_var.get().strip()
            if not name: return messagebox.showerror("Error","Enter a category name")
            if self.data_manager.add_category(category_type,name):
                category_combo['values']=self.data_manager.data['categories'][category_type]; category_var.set(name)
                messagebox.showinfo("Success",f"Category '{name}' added!"); d.destroy()
        btnf=ttk.Frame(f); btnf.grid(row=1,column=0,columnspan=2,pady=20)
        ttk.Button(btnf,text="Add",command=add).pack(side='left',padx=5)
        ttk.Button(btnf,text="Cancel",command=d.destroy).pack(side='left',padx=5)
        e.bind('<Return>',lambda _:add())

    def show_import_dialog(self,parent):
        fp=filedialog.askopenfilename(parent=parent,title="Select CSV",filetypes=[("CSV","*.csv"),("All","*.*")])
        if not fp: return False
        try:
            r=self.data_manager.import_from_csv(fp)
            if r['success']:
                msg=f"Imported {r['imported_count']} transactions"; \
                    msg+=(f"\nFailed: {r['failed_count']}" if r['failed_count'] else '')
                messagebox.showinfo("Import Success",msg)
                if r['errors']: self.show_import_errors(parent,r['errors'])
                return True
            messagebox.showerror("Import Failed","\n".join(r['errors'][:5]) if r['errors'] else "Failed")
        except Exception as e: messagebox.showerror("Error",str(e))
        return False

    def show_import_errors(self,parent,errors):
        d=tk.Toplevel(parent); d.title("Import Errors"); self._center_dialog(d,parent,500,400)
        f=ttk.Frame(d,padding=10); f.pack(fill='both',expand=True)
        ttk.Label(f,text="Import Errors:",font=('Arial',12,'bold')).pack(anchor='w')
        t=tk.Text(f,wrap='word',height=15); s=ttk.Scrollbar(f,command=t.yview); t.configure(yscrollcommand=s.set)
        t.pack(side='left',fill='both',expand=True); s.pack(side='right',fill='y')
        for i,e in enumerate(errors,1): t.insert('end',f"{i}. {e}\n"); t.config(state='disabled')
        ttk.Button(f,text="Close",command=d.destroy).pack(pady=10)

    def show_export_dialog(self,parent):
        fp=filedialog.asksaveasfilename(parent=parent,title="Save CSV",defaultextension=".csv",filetypes=[("CSV","*.csv"),("All","*.*")])
        if not fp: return False
        try:
            if self.data_manager.export_to_csv(fp):
                stats=self.data_manager.get_data_statistics(); messagebox.showinfo("Export Success",f"Exported {stats['total_transactions']} transactions to:\n{fp}"); return True
            messagebox.showwarning("Export Warning","No data to export or failed")
        except Exception as e: messagebox.showerror("Error",str(e))
        return False

    def show_settings_dialog(self,parent):
        d=tk.Toplevel(parent); d.title("Settings"); self._center_dialog(d,parent)
        f=ttk.Frame(d,padding=20); f.pack(fill='both',expand=True)
        currency_var=tk.StringVar(value=self.data_manager.data.get('settings',{}).get('currency','USD'))
        theme_var=tk.StringVar(value=self.data_manager.data.get('settings',{}).get('theme','default'))
        backup_var=tk.BooleanVar(value=self.data_manager.data.get('settings',{}).get('backup_enabled',True))
        for i,(lbl,w) in enumerate([("Currency:",ttk.Combobox(f,textvariable=currency_var,values=('USD','EUR','GBP','JPY','CNY','SGD'),state='readonly')),("Theme:",ttk.Combobox(f,textvariable=theme_var,values=('default','dark','light'),state='readonly'))]):
            ttk.Label(f,text=lbl,font=('Arial',10,'bold')).grid(row=i,column=0,sticky='w',pady=5); w.grid(row=i,column=1,padx=(10,0),sticky='w')
        ttk.Checkbutton(f,text="Enable automatic backups",variable=backup_var).grid(row=2,column=0,columnspan=2,sticky='w',pady=10)
        def save():
            self.data_manager.data['settings']={'currency':currency_var.get(),'theme':theme_var.get(),'backup_enabled':backup_var.get(),'date_format':'%Y-%m-%d'}
            messagebox.showinfo("Success","Settings saved!") if self.data_manager.save_data() else messagebox.showerror("Error","Failed to save")
            d.destroy()
        bf=ttk.Frame(f); bf.grid(row=3,column=0,columnspan=2,pady=30)
        ttk.Button(bf,text="Save",command=save).pack(side='left',padx=5); ttk.Button(bf,text="Cancel",command=d.destroy).pack(side='left',padx=5)

    def show_confirmation_dialog(self,parent,title,msg): return messagebox.askyesno(title,msg,parent=parent)

    def show_about_dialog(self,parent):
        d=tk.Toplevel(parent); d.title("About"); self._center_dialog(d,parent)
        f=ttk.Frame(d,padding=20); f.pack(fill='both',expand=True)
        info="""Smart Personal Finance Management System\nVersion 1.0\n\nFeatures:\n• Transaction management\n• Data visualization\n• Smart analysis\n• Budget tracking\n• Reports\n\n© 2024 All rights reserved"""
        t=tk.Text(f,wrap='word',bg='white',relief='flat'); t.insert('1.0',info); t.config(state='disabled'); t.pack(fill='both',expand=True)
        ttk.Button(f,text="Close",command=d.destroy).pack(pady=10)

if __name__=="__main__":
    class MockDM:
        def __init__(self): self.data={'categories':{'income':['Salary','Bonus'],'expense':['Food','Transport']},'settings':{'currency':'USD','backup_enabled':True}}
        def add_transaction(self,t): print("Adding",t); return True
        def add_category(self,typ,n): self.data['categories'][typ].append(n); return True
    r=tk.Tk(); uim=UserInteractionManager(MockDM())
    for lbl,cmd in [("Add Transaction",uim.show_add_transaction_dialog),("Settings",uim.show_settings_dialog),("About",uim.show_about_dialog)]:
        ttk.Button(r,text=lbl,command=lambda c=cmd:c(r)).pack(pady=5)
    r.mainloop()
