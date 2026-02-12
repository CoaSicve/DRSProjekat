def role_changed_body(name: str, old_role: str, new_role: str) -> str:
    return f"""
    <h2>Promena uloge</h2>
    <p>Zdravo {name},</p>
    <p>Vaša uloga je promenjena.</p>
    <ul>
      <li>Stara uloga: <b>{old_role}</b></li>
      <li>Nova uloga: <b>{new_role}</b></li>
    </ul>
    <p>Prijatan dan,<br/>DRS tim</p>
    """