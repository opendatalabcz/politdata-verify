interface Props {
  message: string
  onClose: () => void
}

export default function RateLimitModal({ message, onClose }: Props) {
  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <span>⚠️ Limit překročen</span>
          <button className="modal-close" onClick={onClose}>✕</button>
        </div>
        <div className="modal-body">
          <p className="rate-limit-msg">{message}</p>
          <p className="rate-limit-sub">
            Pro rozšíření přístupu nás kontaktujte na{' '}
            <a href="mailto:petaherec@gmail.com?subject=PolitData Verify – přístup">
              petaherec@gmail.com
            </a>
            .
          </p>
        </div>
        <div className="modal-footer">
          <button className="btn btn-primary" onClick={onClose}>Rozumím</button>
        </div>
      </div>
    </div>
  )
}
