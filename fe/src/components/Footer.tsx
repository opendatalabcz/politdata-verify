export default function Footer() {
  return (
    <footer className="app-footer">
      <div className="footer-inner">

        {/* Logos */}
        <div className="footer-logos">
          <a href="https://fit.cvut.cz" target="_blank" rel="noopener noreferrer">
            <img
              src="/cvut-fit-logo.svg"
              alt="FIT ČVUT Praha"
              className="footer-logo"
            />
          </a>
          <a href="https://opendatalab.cz" target="_blank" rel="noopener noreferrer">
            <img
              src="https://opendatalab.cz/wp-content/themes/opendatalab/images/logo.svg"
              alt="OpenDataLab"
              className="footer-logo footer-logo-odl"
            />
          </a>
        </div>

        {/* Citation */}
        <div className="footer-citation">
          <p>
            Herčko Petr,{' '}
            <em>Ověřování politických výroků na základě parlamentních a předvolebních dat</em>{' '}
            [online]. Bakalářská práce. Praha: ČVUT, Fakulta informačních technologií
            &amp; OpenDataLab, 2026.
          </p>
          <p className="footer-contact">
            Kontakt:{' '}
            <a href="mailto:petaherec@gmail.com">petaherec@gmail.com</a>
            {' · '}
            <a href="mailto:herckpet@cvut.cz">herckpet@cvut.cz</a>
          </p>
        </div>

        {/* Disclaimer */}
        <div className="footer-disclaimer">
          <p>
            Provozovatel neodpovídá za správnost a úplnost zpracovaných dat a informací,
            ani tato neověřuje a zříká se zodpovědnosti za veškeré škody a újmy,
            které by použitím těchto dat mohly vzniknout.
          </p>
        </div>

      </div>
    </footer>
  )
}
